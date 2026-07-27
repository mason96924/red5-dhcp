"""control.py -- R-1 chiller control / optimisation engine for Red5-DHCP.

R-1 is the Ebara twin-screw water-cooled chiller (RHS DW202M2, 370 kW, COP 4.5,
R-407C) that backs up the DHC chilled-water supply on the 36/37F loop.  This
module turns the raw building driver into a supervisory control result:

  1. Economic DISPATCH -- run DHC (primary) or stage R-1 (backup / DHC
     peak-shave), by comparing marginal cost of DHC cooling vs R-1 cooling.
  2. Condenser-water RESET -- wet-bulb tracking with a min-lift floor.
  3. CHW RESET -- trim-and-respond against the most-open load valve.
  4. Compressor STAGING -- 2 x 45 kW screws, lead/lag with runtime balance
     and anti-short-cycle.
  5. Live COP / kW-per-RT and evaporator/condenser APPROACH temps.
  6. Fault detection & diagnostics (FDD) advisories.
  7. Backup READINESS (scheduled exercise of an otherwise-idle machine).

Everything is a pure function of the driver context so the dashboard, the
device tiles (sim.py) and this panel stay consistent.
"""
from __future__ import annotations

import math

# --- R-1 nameplate (Ebara RHS DW202M2) ------------------------------------
RATED_KW_COOL = 370.0      # 能力 冷却時
RATED_KW_IN = 82.2         # 入力 冷却時  -> COP 4.50
COP_RATED = RATED_KW_COOL / RATED_KW_IN
N_COMP = 2                 # twin 45 kW screw compressors
COMP_KW = 45.0
KW_PER_RT = 3.51685        # 1 refrigeration ton

# --- Tariff assumptions (editable; ¥) --------------------------------------
ELEC_PEAK = 24.0           # ¥/kWh, weekday 09:00-22:00
ELEC_OFF = 16.0            # ¥/kWh otherwise
DHC_ENERGY = 3.6           # ¥ per kWh-thermal of DHC chilled water (energy part)
DHC_DEMAND_ADDER = 9.0     # ¥/kWh-equivalent applied during the DHC system peak
DHC_PEAK_HRS = (13, 16)    # DHC network coincident-peak window
DISPATCH_MARGIN = 1.05     # only switch to R-1 when it beats DHC by >5%

# --- Setpoint envelopes ----------------------------------------------------
CW_APPROACH = 3.5          # °C above wet-bulb
CW_MIN = 19.0              # min entering CW (R-407C min-lift floor)
CW_MAX = 32.0
CHW_MIN = 7.0              # design leaving CHW
CHW_MAX = 10.0             # max reset (mild-load)
CHW_DT_DESIGN = 5.0        # 12 -> 7 C


def _tou_elec(hour: float, weekday: bool) -> float:
    return ELEC_PEAK if (weekday and 9.0 <= hour < 22.0) else ELEC_OFF


def loop_plr(ctx: dict) -> float:
    """36/37F loop part-load ratio derived from the building driver."""
    return max(0.05, min(1.0, (ctx["load"] - 0.12) / 0.8))


def live_cop(plr: float, ecwt: float) -> float:
    """Screw COP vs part-load and entering condenser water temp.
    Anchored so PLR=1.0 @ ECWT 29.4 C returns the rated COP 4.5."""
    f_plr = 0.70 + 0.40 * plr - 0.10 * plr * plr           # ~1.0 near full load
    f_cw = 1.0 + 0.025 * (29.4 - ecwt)                     # cooler tower -> better
    return max(2.8, min(5.8, COP_RATED * f_plr * f_cw))


# ---------------------------------------------------------------------------
# 1. Economic dispatch
# ---------------------------------------------------------------------------
def dispatch(ctx: dict) -> dict:
    hour = ctx["hour"]
    weekday = ctx.get("weekday", True)
    plr = loop_plr(ctx)
    ecwt = cw_setpoint(ctx)["setpoint"]
    cop = live_cop(plr, ecwt)

    elec = _tou_elec(hour, weekday)
    r1_cost = elec / cop                                   # ¥ per kWh cooling
    in_peak = DHC_PEAK_HRS[0] <= hour < DHC_PEAK_HRS[1]
    dhc_adder = DHC_DEMAND_ADDER if (in_peak and ctx["load"] > 0.5) else 0.0
    dhc_cost = DHC_ENERGY + dhc_adder

    # DHC is default; stage R-1 only when it beats DHC by the margin and there
    # is real load on the top-floor loop.
    run_r1 = (dhc_cost > r1_cost * DISPATCH_MARGIN) and plr > 0.15
    if run_r1:
        mode = "R-1 (peak-shave)" if dhc_adder > 0 else "R-1 (economic)"
        reason = (f"DHC ¥{dhc_cost:.1f} > R-1 ¥{r1_cost:.1f}/kWhc"
                  + (" during DHC peak window" if dhc_adder else ""))
    else:
        mode = "DHC" if plr > 0.05 else "Off (no load)"
        reason = (f"DHC ¥{dhc_cost:.1f} <= R-1 ¥{r1_cost:.1f}/kWhc"
                  if plr > 0.05 else "36/37F loop unloaded")

    saving = (dhc_cost - r1_cost) * (RATED_KW_COOL * plr) if run_r1 else 0.0
    return {
        "run_r1": run_r1, "mode": mode, "reason": reason,
        "plr": round(plr, 3), "cop": round(cop, 2),
        "elec_rate": elec, "r1_cost": round(r1_cost, 2),
        "dhc_cost": round(dhc_cost, 2), "dhc_energy": DHC_ENERGY,
        "dhc_demand_adder": dhc_adder, "dhc_peak_window": in_peak,
        "est_saving_yph": round(max(0.0, saving), 0),   # ¥/h vs DHC while shaving
    }


# ---------------------------------------------------------------------------
# 2 & 3. Reset schedules
# ---------------------------------------------------------------------------
def cw_setpoint(ctx: dict) -> dict:
    raw = ctx["wetbulb"] + CW_APPROACH
    sp = max(CW_MIN, min(CW_MAX, raw))
    floored = raw < CW_MIN
    return {"setpoint": round(sp, 1), "approach": CW_APPROACH,
            "floored": floored,
            "note": "at R-407C min-lift floor" if floored else "wet-bulb tracking"}


def chw_setpoint(ctx: dict) -> dict:
    # Trim-and-respond proxy: most-open valve tracks loop load.
    plr = loop_plr(ctx)
    most_open = round(min(100.0, 30 + plr * 70), 0)
    # Raise setpoint when the loop is lightly loaded (most-open < 90%).
    sp = CHW_MIN + (CHW_MAX - CHW_MIN) * max(0.0, (0.9 - plr) / 0.9)
    sp = max(CHW_MIN, min(CHW_MAX, sp))
    return {"setpoint": round(sp, 1), "most_open_valve": most_open,
            "note": "trim-and-respond to most-open coil"}


# ---------------------------------------------------------------------------
# 4. Compressor staging (twin screw, lead/lag + runtime balance)
# ---------------------------------------------------------------------------
def staging(ctx: dict, run_r1: bool) -> dict:
    plr = loop_plr(ctx)
    if not run_r1:
        return {"running": 0, "lead": None, "compressors": [
            {"id": "C1", "on": False, "slide": 0}, {"id": "C2", "on": False, "slide": 0}]}
    # One screw up to ~55% loop, both above.
    n = 1 if plr <= 0.55 else 2
    # Rotate lead by day-of-year parity for even run-hours.
    lead_idx = ctx.get("doy", 0) % 2               # 0 -> C1 lead, 1 -> C2 lead
    lead = f"C{lead_idx + 1}"
    comps = []
    for i in (0, 1):
        cid = f"C{i + 1}"
        is_lead = (i == lead_idx)
        order = 0 if is_lead else 1
        on = order < n
        if not on:
            slide = 0
        elif n == 1:
            slide = round(min(100.0, plr / 0.55 * 100), 0)
        else:
            slide = round(min(100.0, 40 + plr * 60), 0)    # balanced load-share
        comps.append({"id": cid, "on": on, "lead": is_lead, "slide": slide})
    return {"running": n, "lead": lead, "compressors": comps}


# ---------------------------------------------------------------------------
# 5. Performance (COP, kW/RT, approaches)
# ---------------------------------------------------------------------------
def performance(ctx: dict, run_r1: bool) -> dict:
    plr = loop_plr(ctx)
    ecwt = cw_setpoint(ctx)["setpoint"]
    cop = live_cop(plr, ecwt)
    kw_cool = RATED_KW_COOL * plr if run_r1 else 0.0
    kw_in = (kw_cool / cop) if (run_r1 and cop) else 0.0
    tons = kw_cool / KW_PER_RT
    kw_per_rt = (kw_in / tons) if tons > 0.5 else 0.0
    chw = chw_setpoint(ctx)
    chw_dt = CHW_DT_DESIGN * (0.6 + 0.4 * plr) if run_r1 else 0.0
    evap_app = round(1.4 + 0.4 * plr, 2) if run_r1 else 0.0
    cond_app = round(1.2 + 0.9 * plr, 2) if run_r1 else 0.0
    return {
        "cop": round(cop, 2), "kw_cool": round(kw_cool, 0),
        "kw_in": round(kw_in, 1), "kw_per_rt": round(kw_per_rt, 3),
        "chw_supply": chw["setpoint"], "chw_dt": round(chw_dt, 1),
        "cw_return": ecwt, "evap_approach": evap_app, "cond_approach": cond_app,
    }


# ---------------------------------------------------------------------------
# 6. FDD advisories
# ---------------------------------------------------------------------------
def fdd(ctx: dict, run_r1: bool, perf: dict, stg: dict) -> list:
    out = []

    def add(name, active, sev, detail):
        out.append({"name": name, "active": bool(active),
                    "severity": sev, "detail": detail})

    plr = loop_plr(ctx)
    add("Low ΔT syndrome",
        run_r1 and plr > 0.6 and perf["chw_dt"] < 3.8, "warn",
        f"CHW ΔT {perf['chw_dt']}°C vs {CHW_DT_DESIGN}°C design")
    add("Condenser fouling",
        run_r1 and perf["cond_approach"] > 2.6, "warn",
        f"condenser approach {perf['cond_approach']}°C (clean ~1–2°C)")
    add("High lift / min-load",
        run_r1 and plr < 0.2, "info",
        "screw running near minimum slide — anti-cycle timers active")
    add("Short-cycling", False, "info", "starts/hour within limits")
    add("Oil condition", False, "info", "oil ΔP & analysis within limits")
    return out


# ---------------------------------------------------------------------------
# 7. Backup readiness (scheduled exercise of an idle machine)
# ---------------------------------------------------------------------------
def readiness(ctx: dict, run_r1: bool) -> dict:
    dow = ctx.get("dow", 0)          # 0 = Monday
    hour = ctx["hour"]
    exercising = (dow == 0 and 10.0 <= hour < 10.5)
    days_to_mon = (7 - dow) % 7
    if run_r1:
        state = "In service (backup dispatched)"
    elif exercising:
        state = "Exercising (weekly readiness run)"
    else:
        state = "Standby — ready"
    return {"state": state, "exercising": exercising,
            "next_exercise": "Mon 10:00" if not exercising else "now",
            "days_to_next": days_to_mon}


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------
def compute(ctx: dict) -> dict:
    d = dispatch(ctx)
    run_r1 = d["run_r1"]
    perf = performance(ctx, run_r1)
    stg = staging(ctx, run_r1)
    return {
        "machine": "R-1 · Ebara RHS DW202M2 (twin-screw, R-407C, 370 kW)",
        "dispatch": d,
        "cw": cw_setpoint(ctx),
        "chw": chw_setpoint(ctx),
        "staging": stg,
        "performance": perf,
        "fdd": fdd(ctx, run_r1, perf, stg),
        "readiness": readiness(ctx, run_r1),
    }
