"""sim.py -- lightweight, coherent live-value simulator for the DHCP BMS.

There is no real field bus wired up yet, so this module synthesizes plausible
telemetry for every point in the model.  Values are driven by a single
building "driver" (time-of-day occupancy load + outdoor conditions) so the
dashboard reads coherently: e.g. chiller CHW supply sits near 7 C, valve %
tracks load, pumps that pair with a stopped chiller read 0 %.

The DHC network is the PRIMARY cooling/heating source; the local R-1 chiller
(36/37F) is staged as BACKUP only at high load (matches the as-built
チラーバックアップ / 順序切替 logic).
"""
from __future__ import annotations

import math
from datetime import datetime

from points import DEVICES, POINTS, SYSTEMS, PANEL_ORDER, CONTROLLER_META


# ---------------------------------------------------------------------------
# Driver: time-of-day load + outdoor conditions
# ---------------------------------------------------------------------------
def driver(now: datetime) -> dict:
    hour = now.hour + now.minute / 60.0
    # Hotel occupancy load: low overnight, ramps from 06:00, peaks ~15:00.
    hump = max(0.0, math.sin((hour - 6.0) / 18.0 * math.pi))
    load = min(1.0, 0.18 + 0.72 * hump)
    # Outdoor air: warmest ~15:00 (summer-ish base).
    oat = 27.0 + 5.0 * math.cos((hour - 15.0) / 12.0 * math.pi)
    oa_rh = max(38.0, min(88.0, 62.0 - (oat - 27.0) * 2.2))
    wetbulb = _wetbulb(oat, oa_rh)
    heating = now.month in (12, 1, 2, 3)
    occupied = 6.0 <= hour < 24.0
    return {
        "hour": hour, "load": load, "oat": oat, "oa_rh": oa_rh,
        "wetbulb": wetbulb, "heating": heating, "occupied": occupied,
        "minute": now.hour * 60 + now.minute,
    }


def _wetbulb(t: float, rh: float) -> float:
    """Stull (2011) approximation of wet-bulb from dry-bulb + RH."""
    rh = max(1.0, min(100.0, rh))
    return (t * math.atan(0.151977 * math.sqrt(rh + 8.313659))
            + math.atan(t + rh) - math.atan(rh - 1.676331)
            + 0.00391838 * rh ** 1.5 * math.atan(0.023101 * rh)
            - 4.686035)


# ---------------------------------------------------------------------------
# Equipment run-state staging
# ---------------------------------------------------------------------------
def running_state(ctx: dict) -> tuple[dict, set]:
    load = ctx["load"]
    occ = ctx["occupied"]
    heating = ctx["heating"]
    wb = ctx["wetbulb"]
    run: dict = {}
    locked: set = set()

    def stage(prefix, idxs, thresholds):
        """Stage a like-pump group: pump i runs when load exceeds thresholds[i]."""
        for k, i in enumerate(idxs):
            run[f"{prefix}-{i}"] = load > thresholds[min(k, len(thresholds) - 1)]

    # --- DHC intake = PRIMARY source ---
    run["DHC-CHW"] = load > 0.05
    run["DHC-STEAM"] = heating
    run["HWT-1"] = heating            # hot-well active with steam

    # --- Low-rise / high-rise primary CHW pumps (CP-1/CP-2 x3, sequenced) ---
    stage("CP-1", (1, 2, 3), (0.05, 0.45, 0.75))
    stage("CP-2", (1, 2, 3), (0.05, 0.45, 0.75))
    # High-rise INV + changeover pumps
    stage("CP-3", (1, 2), (0.05, 0.65))
    run["CP-6-1"] = load > 0.05       # №1 priority
    run["CP-6-2"] = load > 0.70
    # Kitchen pumps (occupied)
    for p in ("CP-4", "CP-5"):
        run[f"{p}-1"] = occ
        run[f"{p}-2"] = occ and load > 0.6

    # --- Hot-water pumps (HP-1/HP-2 x3): heating season only ---
    for grp in ("HP-1", "HP-2"):
        for i in (1, 2, 3):
            run[f"{grp}-{i}"] = heating and load > (0.05 + 0.30 * (i - 1))
            if not heating:
                locked.add(f"{grp}-{i}")
    # Hot-well pumps: HP-5 condensate-return (with steam), HP-3 kitchen AHU
    for i in (1, 2):
        run[f"HP-5-{i}"] = heating and (i == 1 or load > 0.6)
        run[f"HP-3-{i}"] = occ and (i == 1 or load > 0.6)
        if not heating:
            locked.add(f"HP-5-{i}")

    # --- Condenser water for packaged units + refrigeration (always some) ---
    # CDP-1 (x3) + CDP-2 (x2) lead 24/7 (electrical-room PACs), scale with load.
    run["CDP-1-1"] = True
    run["CDP-1-2"] = load > 0.35
    run["CDP-1-3"] = load > 0.70
    run["CDP-2-1"] = True
    run["CDP-2-2"] = load > 0.55
    cdp_on = sum(1 for k in ("CDP-1-1", "CDP-1-2", "CDP-1-3", "CDP-2-1", "CDP-2-2") if run[k])
    # CT-1/CT-2 cells scale with condenser pumps online.
    ct_cells = ["CT-1-1", "CT-1-2", "CT-2-1", "CT-2-2"]
    for idx, cid in enumerate(ct_cells):
        run[cid] = idx < max(1, min(4, cdp_on - 1))
    run["CT-1"] = True                # tower body (level/treatment) always monitored
    run["CT-2"] = True
    # Winter free-cooling + emergency HX: normally off (enabled cold/low-WB).
    run["EX-1"] = heating and wb < 8.0
    run["EMHX-1"] = False
    run["EMHX-2"] = False

    # --- 36/37F local plant: R-1 is BACKUP, staged only at high load ---
    r1 = load > 0.62
    run["R-1"] = r1
    run["CDP-3-1"] = r1
    run["CDP-3-2"] = r1 and load > 0.85
    run["CT-3-1"] = r1
    run["CT-3"] = True
    run["HEX-1"] = load > 0.05        # DHC HX feeding 36/37F loop (primary path)
    for i in (1, 2, 3):
        run[f"CP-8-{i}"] = load > (0.05 + 0.35 * (i - 1))   # DHC-side pumps
    run["CP-7-1"] = r1                # R-1 CHW pumps only in chiller mode
    run["CP-7-2"] = r1 and load > 0.85
    run["HP-4-1"] = load > 0.05       # 36/37F secondary loop pumps
    run["HP-4-2"] = load > 0.70
    for v in ("EX4", "EXT-1", "EXT-2", "EXT-3"):
        run[v] = True                 # vessels: monitored (level)
    run["CHGV-1"] = r1                # R-1 branch valve open in chiller mode
    run["CHGV-2"] = not r1            # through-main open in DHC bypass mode

    # --- Packaged units: electrical-room PACs run 24/7, others occupied ---
    always_pac = {"PAC-1-1", "PAC-1-2", "PAC-2", "PAC-3", "PAC-4", "PAC-5"}
    for d in DEVICES.values():
        did = d["id"]
        if did.startswith(("PAC-", "PCU-", "PMAC")):
            run[did] = True if did in always_pac else (occ and load > 0.03)

    # --- Lighting: facade at night, common areas when occupied ---
    night = ctx["hour"] < 6.0 or ctx["hour"] >= 18.0
    for d in DEVICES.values():
        did = d["id"]
        if did.startswith("LTG-"):
            run[did] = night if ("NEON" in did or "AVIATION" in did or "BALCONY" in did) else occ

    # Air side.
    for d in DEVICES.values():
        did = d["id"]
        if did.startswith("AC-") or did.startswith("EVU-"):
            run[did] = occ and load > 0.03
        elif did.startswith("FCU-"):
            run[did] = occ
        elif did.startswith(("EF-", "SF-", "RF-")):
            run[did] = None  # resolved after AHUs (interlocked to parent)

    # Fans follow their parent AHU (parent id embedded in the area string).
    for d in DEVICES.values():
        did = d["id"]
        if did.startswith(("EF-", "SF-", "RF-")):
            parent = _fan_parent(d["area"])
            run[did] = bool(run.get(parent, False))

    # Pool filtration: daytime schedule.
    run["POOL-FP"] = 8.0 <= ctx["hour"] < 19.0

    return run, locked


def _fan_parent(area: str) -> str:
    # area is like "Serves AC-7 (Main kitchen)"
    if "AC-" in area:
        try:
            return "AC-" + area.split("AC-", 1)[1].split(" ")[0].strip(")")
        except Exception:
            return ""
    return ""


# ---------------------------------------------------------------------------
# Per-point value synthesis
# ---------------------------------------------------------------------------
def _jitter(tag: str, minute: int, amp: float) -> float:
    """Small deterministic wobble, stable within a minute, keyed by tag."""
    ph = (hash(tag) % 360) * math.pi / 180.0
    return amp * math.sin(minute / 30.0 * math.pi + ph)


def point_value(p: dict, ctx: dict, run) -> dict:
    """Return {'value', 'state', 'display', 'alarm'} for one point."""
    kind = p["kind"]
    suf = p["suffix"]
    load = ctx["load"]
    minute = ctx["minute"]
    on = bool(run) if run is not None else True

    if kind == "status":
        return _status(p, suf, on, ctx)
    if kind == "command":
        return _command(p, suf, on, ctx)
    if kind == "percent":
        return _percent(p, suf, on, ctx)
    if kind == "temp":
        return _temp(p, suf, on, ctx)
    if kind == "rh":
        v = ctx["oa_rh"] if suf in ("OARH", "RH") and p["device_id"] == "OA-STN" else \
            (ctx["oa_rh"] if suf == "OARH" else 46.0 + _jitter(p["tag"], minute, 3))
        return _num(round(v, 1), "%RH")
    if kind == "press":
        heating = ctx["heating"]
        v = (0.68 if heating else 0.20) + _jitter(p["tag"], minute, 0.02)
        return _num(round(v, 3), "MPa")
    if kind == "flow":
        v = round((300 + load * 3200) if on else 0.0, 0)
        return _num(v, "L/min")
    if kind == "power":
        return _power(p, suf, on, ctx)
    if kind == "level":
        v = 55.0 + _jitter(p["tag"], minute, 4)
        return _num(round(v, 1), "%")
    if kind == "energy":
        return _energy(p, ctx)
    return _num(0.0, p["units"])


def _num(v, unit):
    return {"value": float(v), "state": None,
            "display": f"{v:g} {unit}".strip(), "alarm": False}


def _bin(state, on_lbl, off_lbl, alarm=False):
    return {"value": None, "state": bool(state),
            "display": on_lbl if state else off_lbl, "alarm": alarm}


def _status(p, suf, on, ctx):
    if suf == "RUN":
        return _bin(on, "Running", "Stopped")
    if suf == "FLW":
        return _bin(on, "Flow proven", "No flow")
    if suf in ("TRIP",) or suf.endswith("-F") or suf in ("FLT", "FRZ"):
        return _bin(False, "FAULT", "Normal")     # faults clear in the sim
    if suf == "ISOL-ST":
        return _bin(_isol_open(p, ctx), "Open", "Closed")
    if suf == "MODE":
        return _bin(ctx["heating"], "Heating", "Cooling")
    if suf == "LR":
        return _bin(True, "Remote", "Local")
    return _bin(on, "On", "Off")


def _isol_open(p, ctx):
    did = p["device_id"]
    if did.startswith("DHC-STEAM"):
        return ctx["heating"]
    if did.startswith("DHC-CHW"):
        return ctx["load"] > 0.05
    return True


def _command(p, suf, on, ctx):
    if suf in ("ISOL",):
        return _bin(_isol_open(p, ctx), "Open", "Closed")
    if suf == "CMD" and p["device_id"].startswith("CHGV"):
        return _bin(on, "Open", "Closed")
    if suf == "EN":
        return _bin(on, "Enabled", "Disabled")
    if suf in ("MU", "BLD", "EH"):
        return _bin(False, "Open" if suf != "EH" else "On", "Closed" if suf != "EH" else "Off")
    if suf == "FILT-SS":
        return _bin(on, "On", "Off")
    return _bin(on, "On", "Off")


def _percent(p, suf, on, ctx):
    load, minute, heating = ctx["load"], ctx["minute"], ctx["heating"]
    did = p["device_id"]
    v = 0.0
    if suf in ("SPD", "SPDFB"):
        v = (42 + load * 55) if on else 0.0
    elif suf in ("CCV", "CWV"):
        v = (load * 92) if on else 0.0
    elif suf in ("HCV", "HWV", "HUM", "PRV"):
        v = (load * 70) if (on and heating) else (4.0 if suf == "PRV" else 0.0)
    elif suf == "OAD":
        v = (24 + load * 22) if on else 0.0
    elif suf == "DMD":
        v = 100.0 if on else 0.0
    elif suf in ("CV", "CVFB"):          # DHC intake control valve (primary)
        v = (28 + load * 62) if ctx["load"] > 0.05 else 0.0
    elif suf in ("PV", "PVFB"):          # HEX primary valve
        v = (load * 88) if on else 0.0
    elif suf == "MODE":
        v = 0.0
    else:
        v = (load * 80) if on else 0.0
    v = max(0.0, min(100.0, v + (_jitter(p["tag"], minute, 1.5) if v > 0 else 0)))
    return _num(round(v, 1), "%")


def _temp(p, suf, on, ctx):
    j = _jitter(p["tag"], ctx["minute"], 0.25)
    oat = ctx["oat"]
    did = p["device_id"]
    v = 20.0
    if suf in ("CS-T",):
        v = 7.0
    elif suf in ("CR-T",):
        v = 12.0
    elif suf == "WB":
        v = ctx["wetbulb"]
    elif did.startswith("ST-") and suf == "T":
        v = oat
    elif suf in ("CHWST", "P-IN"):
        v = (7.0 if on else 12.0)
    elif suf == "ST":                 # HX/valve/free-cool leaving temp
        v = (7.0 if on else 12.0)
    elif suf in ("CHWRT", "P-OUT", "RT") and did.startswith(("R-1", "HEX", "DHC-CHW")):
        v = 12.0
    elif suf == "S-IN":
        v = 15.0
    elif suf == "S-OUT":
        v = 10.0
    elif suf == "CWRT":
        v = (35.5 if on else oat)
    elif suf == "OAT":
        v = oat
    elif suf == "SAT":
        if not on:
            v = 24.0
        elif p["device_type"].startswith("AHU") and "kitchen" in p["area"].lower():
            v = 9.0
        elif did.startswith("EVU-"):
            v = 16.0
        else:
            v = 14.0
    elif suf == "RAT":
        v = 24.0
    elif suf == "RT":            # FCU zone reference
        v = 24.0
    elif suf == "HTEMP":
        v = (165.0 if ctx["heating"] else 120.0)
    elif suf == "COND-T":
        v = 82.0
    elif did == "OA-STN":
        v = oat
    return _num(round(v + j, 1), "°C")


def _power(p, suf, on, ctx):
    load = ctx["load"]
    did = p["device_id"]
    v = 0.0
    if did.startswith("R-1"):
        v = 335.0 * (0.45 + 0.55 * load) if on else 0.0     # ~370 kW class
    elif did.startswith(("CP-", "CDP-", "HP-")):
        v = (5 + load * 12) if on else 0.0
    elif did.startswith("CT-"):
        v = (2 + load * 9) if on else 0.0
    else:
        v = (load * 8) if on else 0.0
    return _num(round(v, 1), "kW")


def _energy(p, ctx):
    # Monotonic-ish cumulative meter: stable base per tag + daily accumulation.
    base = 10000 + (hash(p["tag"]) % 90000)
    accrued = ctx["minute"] * (2.0 + (hash(p["tag"]) % 7))
    v = round(base + accrued, 0)
    return _num(v, p["units"])


# ---------------------------------------------------------------------------
# Snapshot assembly
# ---------------------------------------------------------------------------
def _device_summary(did, dtype, running, locked, pvals):
    by_suf = {pv["suffix"]: pv for pv in pvals}

    def g(suf):
        return by_suf.get(suf)

    if did.startswith("R-1"):
        if not running:
            return "Off — DHC backup"
        kw = g("KW"); return f"{g('CHWST')['value']:.1f}°C CHWS · {kw['value']:.0f} kW" if kw else "Running"
    if did.startswith(("CP-", "CDP-", "HP-")):
        if locked:
            return "Locked (season)"
        if running and g("SPD"):
            return f"{g('SPD')['value']:.0f}% speed"
        return "Running" if running else ("Off" if running is False else "—")
    if did.startswith("CT-") and "-" in did[3:]:
        return f"fan {g('SPD')['value']:.0f}%" if running and g("SPD") else "Off"
    if did.startswith("CT-"):
        lvl = g("LVL"); return f"basin {lvl['value']:.0f}%" if lvl else "Monitored"
    if did == "HEX-1":
        return f"S-out {g('S-OUT')['value']:.1f}°C" if g("S-OUT") else "Active"
    if did.startswith("EX") or did.startswith("EMHX"):
        so = g("S-OUT") or g("ST"); return f"{so['value']:.1f}°C" if so else ("Enabled" if running else "Off")
    if did.startswith("CHGV"):
        return "R-1 mode" if running else "DHC bypass"
    if did == "HWT-1":
        lvl = g("LVL"); return f"level {lvl['value']:.0f}%" if lvl else "Hot-well"
    if did.startswith("DHC-CHW"):
        cv = g("CV"); return f"valve {cv['value']:.0f}% · {g('CS-T')['value']:.1f}°C" if cv else "Intake"
    if did.startswith("DHC-STEAM"):
        st = g("ISOL-ST")
        return f"{st['display']} steam" if st else "Interface"
    if did.startswith(("PAC-", "PCU-", "PMAC")):
        return "Running" if running else "Off"
    if did.startswith("LTG-"):
        return "On" if running else "Off"
    if did == "REFR-1":
        return "Monitored"
    if did.startswith("AC-"):
        return f"SAT {g('SAT')['value']:.1f}°C" if running and g("SAT") else "Off"
    if did.startswith("EVU-"):
        return f"SAT {g('SAT')['value']:.1f}°C" if running and g("SAT") else "Off"
    if did.startswith("FCU-"):
        return "Enabled" if running else "Disabled"
    if did.startswith("MTR-"):
        pv = pvals[0]; return pv["display"]
    if did.startswith(("EF-", "SF-", "RF-")):
        return "Running" if running else "Off"
    return "—"


def build_snapshot(now: datetime) -> dict:
    ctx = driver(now)
    run, locked = running_state(ctx)

    devices = []
    sys_acc = {}
    total_alarms = 0

    for did, d in DEVICES.items():
        r = run.get(did, None)
        is_locked = did in locked
        pvals = []
        dev_alarms = 0
        for p in d["points"]:
            pv = point_value(p, ctx, r)
            if pv["alarm"]:
                dev_alarms += 1
            pvals.append({
                "tag": p["tag"], "suffix": p["suffix"], "system": p["system"],
                "device_id": did, "device_type": p["device_type"],
                "area": p["area"], "panel": p["panel"],
                "controller": p["controller"], "description": p["description"],
                "io_type": p["io_type"], "units": p["units"], "kind": p["kind"],
                "sp": p["sp"], "trend": p["trend"], "notes": p["notes"],
                **pv,
            })
        total_alarms += dev_alarms

        if dev_alarms:
            status = "alarm"
        elif is_locked:
            status = "standby"
        elif r is True:
            status = "ok"
        elif r is False:
            status = "off"
        else:
            status = "ok"

        summary = _device_summary(did, d["type"], r, is_locked, pvals)
        devices.append({
            "id": did, "type": d["type"], "system": d["system"],
            "area": d["area"], "panel": d["panel"], "controller": d["controller"],
            "running": r, "locked": is_locked, "status": status,
            "summary": summary, "alarms": dev_alarms, "points": pvals,
        })

        acc = sys_acc.setdefault(d["system"], {"devices": 0, "running": 0,
                                               "points": 0, "alarms": 0})
        acc["devices"] += 1
        acc["running"] += 1 if r else 0
        acc["points"] += len(pvals)
        acc["alarms"] += dev_alarms

    systems = [{"name": s, **sys_acc.get(s, {"devices": 0, "running": 0,
                                             "points": 0, "alarms": 0})}
               for s in SYSTEMS]

    return {
        "ts": now.isoformat(),
        "service": "red5-dhcp",
        "driver": {
            "load_pct": round(ctx["load"] * 100, 1),
            "oat_c": round(ctx["oat"], 1),
            "oa_rh": round(ctx["oa_rh"], 1),
            "wetbulb_c": round(ctx["wetbulb"], 1),
            "heating_season": ctx["heating"],
            "occupied": ctx["occupied"],
        },
        "systems": systems,
        "devices": devices,
        "alarms": total_alarms,
        "point_count": len(POINTS),
        "device_count": len(DEVICES),
        "panel_count": len(PANEL_ORDER),
        "controller_count": len(CONTROLLER_META),
    }
