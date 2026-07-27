"""points.py -- structured device / point model for the Red5-DHCP BMS.

The single source of truth for the point list is ``generate_io_list.py`` at the
repo root (the same module that builds the Excel deliverable).  Importing it is
side-effect free -- the ``.xlsx`` is only written under its ``__main__`` guard --
so here we import its ``rows`` / ``controllers`` / ``PANELS`` and reshape them
into panel -> controller -> device -> point objects the API can serve.

Each point is also tagged with a physical ``kind`` (temp / rh / press / flow /
power / percent / level / energy / status / command) derived from its I/O type,
units and tag suffix, which the simulator (``sim.py``) uses to synthesize
plausible live values.
"""
from __future__ import annotations

import os
import sys
from collections import OrderedDict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import generate_io_list as _g  # noqa: E402  (side-effect free import)

# Panel id -> (description, location, served)
PANEL_META = {p[0]: {"description": p[1], "location": p[2], "served": p[3]}
              for p in _g.PANELS}
PANEL_ORDER = [p[0] for p in _g.PANELS]

# Controller id -> {panel, devices[]}
CONTROLLER_META = {c[0]: {"panel": c[1],
                          "devices": [d.strip() for d in c[2].split(",") if d.strip()]}
                   for c in _g.controllers}


def _point_kind(tag: str, io: str, units: str) -> str:
    """Classify a point into a physical quantity for the simulator."""
    suffix = tag.split(".", 1)[1] if "." in tag else tag
    if io == "BO":
        return "command"
    if io == "BI":
        return "status"
    if io == "AO":
        return "percent"          # every AO in this model is a % command
    # AI -----------------------------------------------------------------
    u = (units or "").strip()
    if u in ("°C", "C"):
        return "temp"
    if u == "%RH":
        return "rh"
    if u == "MPa":
        return "press"
    if u == "L/min":
        return "flow"
    if u == "kW":
        return "power"
    if u in ("GJ", "kWh", "m³"):
        return "energy"
    if u == "%":
        return "level" if suffix.startswith("LVL") else "percent"
    return "level"


def _build():
    points = []
    devices = OrderedDict()
    for r in _g.rows:
        tag = r["Point Tag"]
        did = r["Device ID"]
        kind = _point_kind(tag, r["I/O Type"], r["Units"])
        suffix = tag.split(".", 1)[1] if "." in tag else tag
        p = {
            "tag": tag,
            "suffix": suffix,
            "system": r["System"],
            "device_id": did,
            "device_type": r["Device Type"],
            "area": r["Area / Served"],
            "panel": r["Panel"],
            "controller": r["Controller"],
            "description": r["Point Description"],
            "io_type": r["I/O Type"],
            "signal": r["Signal / Range"],
            "units": r["Units"],
            "sp": bool(r["SP/Sched"]),
            "alarm_cfg": bool(r["Alarm"]),
            "trend": bool(r["Trend"]),
            "notes": r["Notes / Basis"],
            "kind": kind,
        }
        points.append(p)
        if did not in devices:
            devices[did] = {
                "id": did,
                "type": r["Device Type"],
                "system": r["System"],
                "area": r["Area / Served"],
                "panel": r["Panel"],
                "controller": r["Controller"],
                "points": [],
            }
        devices[did]["points"].append(p)
    return points, devices


POINTS, DEVICES = _build()

# System -> ordered list of device ids (for grouping in the UI)
SYSTEMS = OrderedDict()
for _d in DEVICES.values():
    SYSTEMS.setdefault(_d["system"], []).append(_d["id"])


def panel_summary():
    out = []
    for pid in PANEL_ORDER:
        meta = PANEL_META[pid]
        ctrls = [c for c, m in CONTROLLER_META.items() if m["panel"] == pid]
        npts = sum(1 for p in POINTS if p["panel"] == pid)
        out.append({"id": pid, **meta, "controllers": len(ctrls),
                    "point_count": npts})
    return out
