"""sim.py -- lightweight, coherent live-value simulator for the DHCP BMS.

There is no real field bus wired up yet, so this module synthesizes plausible
telemetry for every point in the model.  Values are driven by a single
building "driver" (time-of-day occupancy load + outdoor conditions) so the
dashboard reads coherently: e.g. chiller CHW supply sits near 7 C, valve %
tracks load, pumps that pair with a stopped chiller read 0 %.

The DHC network is the PRIMARY cooling/heating source; the local RC-1 chillers
are staged as BACKUP only at high load (matches the as-built 順序切替 logic).
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
    run: dict = {}
    locked: set = set()

    # Chillers -- BACKUP: staged only above 50% load.
    if load < 0.50:
        n_chill = 0
    else:
        n_chill = min(3, 1 + int((load - 0.50) / 0.17))
    for i in (1, 2, 3):
        run[f"RC-1-{i}"] = i <= n_chill
        run[f"CP-8-{i}"] = i <= n_chill        # primary CHW pump paired 1:1
        run[f"CWP-{i}"] = i <= n_chill         # condenser pump paired 1:1

    # Cooling-tower cells scale with chillers online.
    cells = 0 if n_chill == 0 else min(4, n_chill * 2)
    order = [("CT-1-1"), ("CT-1-2"), ("CT-2-1"), ("CT-2-2")]
    for idx, cid in enumerate(order):
        run[cid] = idx < cells

    # HEX-1 (DHC chilled-water plate HX) is the primary path -- active whenever
    # there is any cooling demand.  The DHC intakes track the same demand;
    # steam intakes follow the heating season.
    run["HEX-1"] = load > 0.05
    run["DHC-CHW-L"] = load > 0.05
    run["DHC-CHW-H"] = load > 0.05
    run["DHC-STEAM-L"] = heating
    run["DHC-STEAM-H"] = heating

    # Secondary CHW distribution pumps: lead always on when occupied, lag on
    # at higher load.
    run["CP-7-1"] = load > 0.08
    run["CP-7-2"] = load > 0.60

    # Hot-water pumps: heating season only.
    for i in (1, 2):
        run[f"HWP-{i}"] = heating and load > 0.10
        if not heating:
            locked.add(f"HWP-{i}")

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
    if suf == "SEQ":
        return _bin(True, "DHC lead", "Chiller")
    if suf == "EN":
        return _bin(ctx["occupied"], "Enabled", "Disabled")
    if suf in ("MU", "BLD"):
        return _bin(False, "Open", "Closed")
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
    if suf in ("CHWST", "P-IN", "ST"):
        v = (7.0 if on else 12.0)
    elif suf in ("CHWRT", "P-OUT", "RT") and did.startswith(("RC-", "HEX", "DHC-CHW")):
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
    if did.startswith("RC-1"):
        v = 335.0 * (0.45 + 0.55 * load) if on else 0.0     # ~370 kW class
    elif did.startswith(("CP-8", "CWP", "CP-7", "HWP")):
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

    if did.startswith("RC-1"):
        if not running:
            return "Off — DHC backup"
        kw = g("KW"); return f"{g('CHWST')['value']:.1f}°C CHWS · {kw['value']:.0f} kW" if kw else "Running"
    if did.startswith(("CP-8", "CP-7", "CWP", "HWP")):
        if locked:
            return "Locked (season)"
        return f"{g('SPD')['value']:.0f}% speed" if running and g("SPD") else ("Off" if running is False else "—")
    if did.startswith("CT-"):
        return f"fan {g('SPD')['value']:.0f}%" if running and g("SPD") else "Off"
    if did == "HEX-1":
        return f"S-out {g('S-OUT')['value']:.1f}°C" if g("S-OUT") else "Active"
    if did.startswith("DHC-CHW"):
        cv = g("CV"); return f"valve {cv['value']:.0f}% · {g('ST')['value']:.1f}°C" if cv else "Intake"
    if did.startswith("DHC-STEAM"):
        st = g("ISOL-ST")
        return f"{st['display']} · {g('HTEMP')['value']:.0f}°C" if st else "Interface"
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
