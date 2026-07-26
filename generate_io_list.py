"""generate_io_list.py -- Red5-DHCP BMS I/O list + panel / controller schedule.

Builds a comprehensive multi-sheet Excel workbook for the ANA InterContinental
Tokyo District-Heating-&-Cooling (DHC) connected BMS, derived from the as-built
drawings (M-01 equipment schedule), the Azbil ESCO scope (共-01), and the
air-side operating schedules (空調機スケジュール_20251127.xlsx).

Equipment CONFIRMED from the documents:
  * RC-1  water-cooled screw modular chillers x3 (370 kW, CHW 12->7C, CW 32->37C)
  * CP-8  primary chilled-water pumps x3 (VFD, 1-per-chiller)
  * HEX-1 SUS plate heat exchanger (395 kW; 1' 7->12C / 2' 15->10C)
  * Cooling towers + condenser-water pumps
  * DHC steam mains: low-rise (B2F) and high-rise (rooftop/PH)
  * AC-1..27  public / kitchen air-handling units
  * EVU-1..15 outdoor-air / make-up-air units (guest-room + function zones)
  * FCU (36/37F, 4-pipe + free cooling)
  * Kitchen ventilators / exhaust-supply-return fans (EF/SF/RF)
  * Main energy meters (electricity, gas, city water, DHC steam/chilled)

Inferred items (secondary distribution pumps, hot-water pumps, FCU quantity)
are flagged "INFERRED" in the Notes/Basis column -- confirm against as-builts.

Run:  .venv/bin/python generate_io_list.py
Out:  Red5-DHCP_BMS_IO_List.xlsx
"""
from __future__ import annotations

import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "Red5-DHCP_BMS_IO_List.xlsx")

# --------------------------------------------------------------------------
# Panels (distributed DDC local control panels + central)
# --------------------------------------------------------------------------
PANELS = [
    ("BMS-CENTRAL", "Central monitoring server (中央監視)", "B2F Central Monitoring Rm",
     "Whole-building supervisory, alarms, trends, schedules, energy"),
    ("LCP-PH", "Heat-source & high-rise field panel", "PH Machine Room",
     "Chillers, primary/condenser pumps, cooling towers, HEX-1, high-rise DHC steam, PH/high-rise AHUs & OAUs"),
    ("LCP-B2", "Low-rise heat-interface & basement panel", "B2F Machine Room",
     "Low-rise DHC steam interface, secondary/hot-water pumps, pool filtration, basement AHUs, main meters"),
    ("LCP-1F", "1F–2F air-side panel", "1F EPS/AHU Room",
     "AC-7, EVU-1..3 (1F ceremony/banquet/lobby)"),
    ("LCP-2F", "2F air-side panel", "2F AHU Room",
     "AC-8..13, EVU-4..6 (atrium, Prominence, offices/tenants)"),
    ("LCP-3F", "3F air-side panel", "3F AHU Room",
     "AC-14..16, EVU-7 (Unkai/Karin/DaVinci, chapel)"),
    ("LCP-4F", "4F–5F air-side panel", "4F AHU Room",
     "AC-17..21, EVU-8..10 (kitchens, low-rise guest-room OAUs)"),
]

# device -> panel resolver by device id
def panel_for(dev_id: str) -> str:
    ac = None
    if dev_id.startswith("AC-"):
        ac = int(dev_id.split("-")[1])
        if ac in (22, 23, 24, 25, 27): return "LCP-PH"
        if ac in (17, 18, 19, 20, 21): return "LCP-4F"
        if ac in (14, 15, 16): return "LCP-3F"
        if ac in (8, 9, 10, 11, 12, 13): return "LCP-2F"
        if ac == 7: return "LCP-1F"
        return "LCP-B2"  # AC-1..6, AC-26
    if dev_id.startswith("EVU-"):
        n = int(dev_id.split("-")[1])
        if n in (11, 12, 13, 14, 15): return "LCP-PH"
        if n in (8, 9, 10): return "LCP-4F"
        if n == 7: return "LCP-3F"
        if n in (4, 5, 6): return "LCP-2F"
        return "LCP-1F"  # 1..3
    return "LCP-PH"

# --------------------------------------------------------------------------
# Signal-type shorthands
# --------------------------------------------------------------------------
AI, AO, BI, BO = "AI", "AO", "BI", "BO"
SIG = {
    "temp":   ("4-20mA", "°C"),
    "rh":     ("4-20mA", "%RH"),
    "press":  ("4-20mA", "MPa"),
    "flow":   ("4-20mA", "L/min"),
    "kw":     ("4-20mA", "kW"),
    "pct":    ("0-10V",  "%"),
    "pctfb":  ("4-20mA", "%"),
    "level":  ("4-20mA", "%"),
    "status": ("DI dry contact", "-"),
    "cmd":    ("DO relay", "-"),
    "pulse":  ("Pulse/Modbus", "unit"),
}

rows = []   # each: dict of columns

def add(tag, system, dev, dtype, area, desc, io, sigkey, units=None,
        sp="", alarm="", trend="", notes=""):
    sig, unit = SIG[sigkey]
    rows.append({
        "Point Tag": tag, "System": system, "Device ID": dev,
        "Device Type": dtype, "Area / Served": area,
        "Panel": panel_for(dev) if dev[:3] in ("AC-", "EVU") else PANEL_HINT.get(dev, "LCP-PH"),
        "Controller": "",  # filled later
        "Point Description": desc, "I/O Type": io,
        "Signal / Range": sig, "Units": units or unit,
        "SP/Sched": sp, "Alarm": alarm, "Trend": trend, "Notes / Basis": notes,
    })

# heat-source / plant device -> panel hint
PANEL_HINT = {}

# --------------------------------------------------------------------------
# Device inventories
# --------------------------------------------------------------------------
AC_AREAS = {
    1: "B3-4F service elevator hall", 2: "Mid banquet / B1F back corridor / F&B office",
    3: "B1F guest lift lobby & anteroom", 4: "B1F banquet lobby",
    5: "Guardmanger & Bakery kitchen", 6: "C kitchen", 7: "Main kitchen",
    8: "Cascade Cafe hall", 9: "Cascade kitchen", 10: "Atrium lobby/lounge",
    11: "Prominence I", 12: "Prominence II", 13: "Prominence III",
    14: "Unkai hall", 15: "Karin/Kenzan kitchen", 16: "DaVinci kitchen",
    17: "Unkai kitchen", 18: "Steakhouse kitchen", 19: "Steakhouse hall",
    20: "Poolside snack/pantry (4F)", 21: "5F staff canteen kitchen",
    22: "PG/Mixx kitchen (36F)", 23: "Akasaka kitchen (37F)",
    24: "Akasaka hall / Libra / Aries", 25: "Sirius hall & kitchen",
    26: "Banquet-service office (B2F)", 27: "Club Lounge (35F) - 4-pipe",
}
AC_KITCHEN = {5, 6, 7, 9, 15, 16, 17, 18, 21, 22, 23}   # supply-air low-temp kitchens
AC_NO_INV = {1, 2, 3, 8, 9}                              # "制御無し" / INV故障 per schedule
AC_HAS_HEAT = set(range(1, 28)) - {2, 3, 4}              # most have steam heat; a few cool-only
AC_HUMID = {10, 14, 19, 24, 27}                          # halls/lounges with humidification

EVU_AREAS = {
    1: "1F ceremony/photo/dress/beauty/corridor", 2: "1F small banquet/corridor/store",
    3: "Banquet entrance lobby & bell room", 4: "2F office & CPU room",
    5: "2F tenants/shops", 6: "Prominence (B1F precool)",
    7: "3F Karin/Kenzan/DaVinci/chapel", 8: "Low-rise guest rooms N (6-20F)",
    9: "Low-rise guest rooms SE (6-20F)", 10: "Low-rise guest rooms SW (6-20F)",
    11: "High-rise guest rooms N (21-35F)", 12: "High-rise guest rooms SE (21-35F)",
    13: "High-rise guest rooms SW (21-35F)", 14: "36F office/Mixx",
    15: "36F PG hall/rooms/pantry, Mixx bar/hall",
}
EVU_NO_INV = {1, 2, 3, 4, 5, 6, 7, 14, 15}   # "制御無しの為変更不可" per schedule

# fans: (tag, parent AC, inv?)
FANS = [
    ("SF-6", 1, False), ("EF-2-1", 8, False), ("EF-28", 5, False),
    ("EF-32", 6, False), ("EF-33", 6, False), ("EF-41", 7, False), ("EF-42", 7, False),
    ("EF-46", 9, False), ("EF-47", 9, False), ("EF-54", 17, False), ("EF-55", 17, False),
    ("EF-56", 14, False), ("EF-57", 18, False), ("EF-58", 18, False),
    ("EF-59", 19, False), ("EF-59-2", 19, False), ("EF-60", 15, False),
    ("EF-61", 16, False), ("EF-62", 16, False), ("EF-67", 20, False),
    ("EF-69", 21, False), ("EF-70", 21, True), ("EF-71", 20, False),
    ("EF-76", 15, False), ("EF-77", 15, False), ("EF-82", 22, False),
    ("EF-83", 22, True), ("EF-84", 23, False), ("EF-85", 24, False),
    ("EF-86", 24, False), ("EF-89", 25, False), ("EF-97", 26, False),
    ("EF-98", 27, False), ("RF-7", 3, False), ("RF-8", 4, False), ("RF-9", 26, False),
]

# FCU zones (36/37F 4-pipe) -- quantity INFERRED, confirm against as-built
FCU = [(f"FCU-36-{i}", "36F guest/office zone", "LCP-PH") for i in range(1, 5)] + \
      [(f"FCU-37-{i}", "37F Club/guest zone", "LCP-PH") for i in range(1, 5)]

# --------------------------------------------------------------------------
# Point templates
# --------------------------------------------------------------------------
def chiller_points(dev, area):
    PANEL_HINT[dev] = "LCP-PH"
    add(f"{dev}.RUN", "Heat source", dev, "Water-cooled chiller", area, "Run status", BI, "status", alarm="", trend="Y")
    add(f"{dev}.TRIP", "Heat source", dev, "Water-cooled chiller", area, "Common fault / trip", BI, "status", alarm="Y")
    add(f"{dev}.LR", "Heat source", dev, "Water-cooled chiller", area, "Local/Remote status", BI, "status")
    add(f"{dev}.SS", "Heat source", dev, "Water-cooled chiller", area, "Start/Stop command", BO, "cmd", sp="Y", notes="Lead/lag staged")
    add(f"{dev}.DMD", "Heat source", dev, "Water-cooled chiller", area, "Capacity/demand limit", AO, "pct", sp="Y", notes="Demand-limit / soft-load")
    add(f"{dev}.CHWST", "Heat source", dev, "Water-cooled chiller", area, "CHW supply (leaving) temp", AI, "temp", alarm="Y", trend="Y", notes="Design 7°C")
    add(f"{dev}.CHWRT", "Heat source", dev, "Water-cooled chiller", area, "CHW return (entering) temp", AI, "temp", trend="Y", notes="Design 12°C")
    add(f"{dev}.CWRT", "Heat source", dev, "Water-cooled chiller", area, "Condenser water leaving temp", AI, "temp", trend="Y")
    add(f"{dev}.KW", "Heat source", dev, "Water-cooled chiller", area, "Electrical input power", AI, "kw", trend="Y", notes="For COP / kW-per-ton")
    add(f"{dev}.FLW", "Heat source", dev, "Water-cooled chiller", area, "Evaporator flow proof", BI, "status", alarm="Y")

def cwpump_points(dev, area):
    PANEL_HINT[dev] = "LCP-PH"
    add(f"{dev}.RUN", "Heat source", dev, "Condenser-water pump", area, "Run status", BI, "status", trend="Y")
    add(f"{dev}.TRIP", "Heat source", dev, "Condenser-water pump", area, "Fault", BI, "status", alarm="Y")
    add(f"{dev}.SS", "Heat source", dev, "Condenser-water pump", area, "Start/Stop command", BO, "cmd", notes="Interlock w/ chiller")
    add(f"{dev}.KW", "Heat source", dev, "Condenser-water pump", area, "Power", AI, "kw", trend="Y")
    add(f"{dev}.FLW", "Heat source", dev, "Condenser-water pump", area, "Flow/DP proof", BI, "status", alarm="Y")

def vfd_pump_points(dev, dtype, area, sysname, notes_dp=""):
    add(f"{dev}.RUN", sysname, dev, dtype, area, "Run status", BI, "status", trend="Y")
    add(f"{dev}.TRIP", sysname, dev, dtype, area, "VFD/pump fault", BI, "status", alarm="Y")
    add(f"{dev}.SS", sysname, dev, dtype, area, "Start/Stop command", BO, "cmd")
    add(f"{dev}.SPD", sysname, dev, dtype, area, "VFD speed command", AO, "pct", sp="Y", notes=notes_dp)
    add(f"{dev}.SPDFB", sysname, dev, dtype, area, "VFD speed feedback", AI, "pctfb", trend="Y")
    add(f"{dev}.KW", sysname, dev, dtype, area, "Power", AI, "kw", trend="Y")
    add(f"{dev}.FLW", sysname, dev, dtype, area, "Flow/DP proof", BI, "status", alarm="Y")

def tower_points(dev, area):
    PANEL_HINT[dev] = "LCP-PH"
    add(f"{dev}.RUN", "Heat source", dev, "Cooling tower cell", area, "Fan run status", BI, "status", trend="Y")
    add(f"{dev}.TRIP", "Heat source", dev, "Cooling tower cell", area, "Fan fault", BI, "status", alarm="Y")
    add(f"{dev}.SS", "Heat source", dev, "Cooling tower cell", area, "Fan start/stop", BO, "cmd")
    add(f"{dev}.SPD", "Heat source", dev, "Cooling tower cell", area, "Fan VFD speed command", AO, "pct", sp="Y", notes="Wet-bulb + approach reset")
    add(f"{dev}.SPDFB", "Heat source", dev, "Cooling tower cell", area, "Fan speed feedback", AI, "pctfb", trend="Y")
    add(f"{dev}.LVL", "Heat source", dev, "Cooling tower cell", area, "Basin water level", AI, "level", alarm="Y")
    add(f"{dev}.MU", "Heat source", dev, "Cooling tower cell", area, "Make-up water valve", BO, "cmd")
    add(f"{dev}.BLD", "Heat source", dev, "Cooling tower cell", area, "Bleed/blowdown valve", BO, "cmd")

def hex_points(dev, area):
    PANEL_HINT[dev] = "LCP-PH"
    add(f"{dev}.P-IN", "Heat source", dev, "Plate heat exchanger", area, "Primary inlet temp", AI, "temp", trend="Y", notes="Design 7°C")
    add(f"{dev}.P-OUT", "Heat source", dev, "Plate heat exchanger", area, "Primary outlet temp", AI, "temp", trend="Y", notes="Design 12°C")
    add(f"{dev}.S-IN", "Heat source", dev, "Plate heat exchanger", area, "Secondary inlet temp", AI, "temp", trend="Y", notes="Design 15°C")
    add(f"{dev}.S-OUT", "Heat source", dev, "Plate heat exchanger", area, "Secondary outlet (supply) temp", AI, "temp", sp="Y", alarm="Y", trend="Y", notes="Design 10°C; reset in mild wx")
    add(f"{dev}.S-FLW", "Heat source", dev, "Plate heat exchanger", area, "Secondary supply flow", AI, "flow", trend="Y")
    add(f"{dev}.PV", "Heat source", dev, "Plate heat exchanger", area, "Primary control valve", AO, "pct", sp="Y", notes="Modulate to hold S-OUT")
    add(f"{dev}.PVFB", "Heat source", dev, "Plate heat exchanger", area, "Primary valve position fb", AI, "pctfb")

def steam_points(dev, area, tier):
    PANEL_HINT[dev] = "LCP-PH" if tier == "high" else "LCP-B2"
    add(f"{dev}.HPRESS", "DHC interface", dev, "DHC steam interface", area, "Steam header pressure", AI, "press", alarm="Y", trend="Y")
    add(f"{dev}.HTEMP", "DHC interface", dev, "DHC steam interface", area, "Steam header temp", AI, "temp", trend="Y")
    add(f"{dev}.PRV", "DHC interface", dev, "DHC steam interface", area, "Pressure-reducing / control valve", AO, "pct", sp="Y")
    add(f"{dev}.ISOL", "DHC interface", dev, "DHC steam interface", area, "Main isolation valve open/close", BO, "cmd", sp="Y", notes="Season enable + OA lockout")
    add(f"{dev}.ISOL-ST", "DHC interface", dev, "DHC steam interface", area, "Isolation valve status", BI, "status", alarm="Y")
    add(f"{dev}.COND-T", "DHC interface", dev, "DHC steam interface", area, "Condensate temp", AI, "temp")
    add(f"{dev}.ENERGY", "DHC interface", dev, "DHC steam interface", area, "Steam energy meter", AI, "pulse", units="GJ", trend="Y", notes="For thermal-demand control")

def ahu_points(n):
    dev = f"AC-{n}"
    area = AC_AREAS[n]
    add(f"{dev}.RUN", "Air side", dev, "AHU (public/kitchen)", area, "Supply fan run status", BI, "status", trend="Y")
    add(f"{dev}.TRIP", "Air side", dev, "AHU (public/kitchen)", area, "Supply fan fault", BI, "status", alarm="Y")
    add(f"{dev}.SS", "Air side", dev, "AHU (public/kitchen)", area, "Supply fan start/stop", BO, "cmd", sp="Y", notes="Time/event schedule; banquet 'occ by event'")
    if n not in AC_NO_INV:
        add(f"{dev}.SPD", "Air side", dev, "AHU (public/kitchen)", area, "Supply fan VFD (INV) speed", AO, "pct", sp="Y", notes="INV output schedule 0.4-1.0")
        add(f"{dev}.SPDFB", "Air side", dev, "AHU (public/kitchen)", area, "Supply fan speed feedback", AI, "pctfb", trend="Y")
    else:
        add(f"{dev}.SPD", "Air side", dev, "AHU (public/kitchen)", area, "Supply fan speed (fixed)", AO, "pct", notes="INFERRED / no INV control per schedule")
    add(f"{dev}.SAT", "Air side", dev, "AHU (public/kitchen)", area, "Supply air temp", AI, "temp", sp="Y", alarm="Y", trend="Y",
        notes="Kitchen SAT 5-12°C" if n in AC_KITCHEN else "SAT/RAT setpoint schedule")
    add(f"{dev}.RAT", "Air side", dev, "AHU (public/kitchen)", area, "Return air temp", AI, "temp", trend="Y")
    add(f"{dev}.CCV", "Air side", dev, "AHU (public/kitchen)", area, "Cooling coil (CHW) valve", AO, "pct", sp="Y", notes="PID to SAT; zero-energy band")
    if n in AC_HAS_HEAT:
        add(f"{dev}.HCV", "Air side", dev, "AHU (public/kitchen)", area, "Heating coil (steam) valve", AO, "pct", sp="Y", notes="Season enable; deadband vs CCV")
    if n in AC_HUMID:
        add(f"{dev}.HUM", "Air side", dev, "AHU (public/kitchen)", area, "Steam humidifier valve", AO, "pct", sp="Y")
        add(f"{dev}.RH", "Air side", dev, "AHU (public/kitchen)", area, "Return/space humidity", AI, "rh", trend="Y")
    add(f"{dev}.FLT", "Air side", dev, "AHU (public/kitchen)", area, "Filter dirty (DP)", BI, "status", alarm="Y")
    add(f"{dev}.OAD", "Air side", dev, "AHU (public/kitchen)", area, "Outdoor-air damper", AO, "pct", sp="Y")
    if n in AC_HAS_HEAT:
        add(f"{dev}.FRZ", "Air side", dev, "AHU (public/kitchen)", area, "Freeze protection stat", BI, "status", alarm="Y")

def evu_points(n):
    dev = f"EVU-{n}"
    area = EVU_AREAS[n]
    add(f"{dev}.RUN", "Air side", dev, "Outdoor-air unit (OAU)", area, "Supply fan run status", BI, "status", trend="Y")
    add(f"{dev}.TRIP", "Air side", dev, "Outdoor-air unit (OAU)", area, "Supply fan fault", BI, "status", alarm="Y")
    add(f"{dev}.SS", "Air side", dev, "Outdoor-air unit (OAU)", area, "Supply fan start/stop", BO, "cmd", sp="Y", notes="Time schedule; night setback")
    if n not in EVU_NO_INV:
        add(f"{dev}.SPD", "Air side", dev, "Outdoor-air unit (OAU)", area, "Supply fan VFD (INV) speed", AO, "pct", sp="Y", notes="INV schedule; demand vent")
        add(f"{dev}.SPDFB", "Air side", dev, "Outdoor-air unit (OAU)", area, "Supply fan speed feedback", AI, "pctfb", trend="Y")
    else:
        add(f"{dev}.SPD", "Air side", dev, "Outdoor-air unit (OAU)", area, "Supply fan speed (fixed)", AO, "pct", notes="No INV control per schedule")
    add(f"{dev}.SAT", "Air side", dev, "Outdoor-air unit (OAU)", area, "Supply (off-coil) air temp", AI, "temp", sp="Y", alarm="Y", trend="Y", notes="Seasonal SAT reset")
    add(f"{dev}.OAT", "Air side", dev, "Outdoor-air unit (OAU)", area, "Outdoor-air temp (unit inlet)", AI, "temp", trend="Y")
    add(f"{dev}.OARH", "Air side", dev, "Outdoor-air unit (OAU)", area, "Outdoor-air humidity", AI, "rh", trend="Y")
    add(f"{dev}.CCV", "Air side", dev, "Outdoor-air unit (OAU)", area, "Cooling coil (CHW) valve", AO, "pct", sp="Y")
    add(f"{dev}.HCV", "Air side", dev, "Outdoor-air unit (OAU)", area, "Heating coil (steam) valve", AO, "pct", sp="Y", notes="Season enable; deadband")
    add(f"{dev}.HUM", "Air side", dev, "Outdoor-air unit (OAU)", area, "Steam humidifier valve", AO, "pct", sp="Y")
    add(f"{dev}.FLT", "Air side", dev, "Outdoor-air unit (OAU)", area, "Filter dirty (DP)", BI, "status", alarm="Y")
    add(f"{dev}.FRZ", "Air side", dev, "Outdoor-air unit (OAU)", area, "Freeze protection stat", BI, "status", alarm="Y")

def fcu_points(dev, area, panel):
    PANEL_HINT[dev] = panel
    add(f"{dev}.SS", "Air side", dev, "FCU (4-pipe)", area, "On/Off + fan speed", BO, "cmd", sp="Y", notes="INFERRED qty; 4-pipe + free cooling")
    add(f"{dev}.RUN", "Air side", dev, "FCU (4-pipe)", area, "Run status", BI, "status")
    add(f"{dev}.ST", "Air side", dev, "FCU (4-pipe)", area, "Space temp", AI, "temp", sp="Y", trend="Y")
    add(f"{dev}.CCV", "Air side", dev, "FCU (4-pipe)", area, "Cooling valve", AO, "pct", sp="Y")
    add(f"{dev}.HCV", "Air side", dev, "FCU (4-pipe)", area, "Heating valve", AO, "pct", sp="Y", notes="Deadband vs cooling")
    add(f"{dev}.TRIP", "Air side", dev, "FCU (4-pipe)", area, "Fault", BI, "status", alarm="Y")

def fan_points(tag, parent_ac, inv):
    area = f"Serves AC-{parent_ac} ({AC_AREAS.get(parent_ac,'')})"
    PANEL_HINT[tag] = panel_for(f"AC-{parent_ac}")
    add(f"{tag}.SS", "Ventilation", tag, "Exhaust/supply fan", area, "Start/Stop command", BO, "cmd", sp="Y", notes="Interlock w/ parent AHU")
    add(f"{tag}.RUN", "Ventilation", tag, "Exhaust/supply fan", area, "Run status", BI, "status", trend="Y")
    add(f"{tag}.TRIP", "Ventilation", tag, "Exhaust/supply fan", area, "Fault", BI, "status", alarm="Y")
    if inv:
        add(f"{tag}.SPD", "Ventilation", tag, "Exhaust/supply fan", area, "VFD (INV) speed command", AO, "pct", sp="Y")
        add(f"{tag}.SPDFB", "Ventilation", tag, "Exhaust/supply fan", area, "VFD speed feedback", AI, "pctfb")

def meter_points():
    meters = [
        ("MTR-ELEC-MAIN", "Main electricity (kWh)", "kWh", "LCP-B2"),
        ("MTR-GAS-MAIN", "City gas (m³)", "m³", "LCP-B2"),
        ("MTR-WATER-MAIN", "City water (m³)", "m³", "LCP-B2"),
        ("MTR-DHC-STEAM-L", "DHC steam energy - low-rise", "GJ", "LCP-B2"),
        ("MTR-DHC-STEAM-H", "DHC steam energy - high-rise", "GJ", "LCP-PH"),
        ("MTR-DHC-CHW", "DHC chilled-water energy", "GJ", "LCP-B2"),
        ("MTR-CHILLER-KWH", "Chiller plant sub-meter", "kWh", "LCP-PH"),
        ("MTR-AHU-KWH", "AHU/OAU fans sub-meter", "kWh", "LCP-B2"),
    ]
    for tag, desc, unit, panel in meters:
        PANEL_HINT[tag] = panel
        add(f"{tag}", "Metering", tag, "Energy meter", "Whole building", desc, AI, "pulse", units=unit, trend="Y",
            notes="Integrating meter; thermal-demand & peak limiting")

def common_points():
    PANEL_HINT["OA-STN"] = "LCP-PH"
    add("OA-STN.T", "Common", "OA-STN", "Outdoor-air station", "Rooftop", "Outdoor-air dry-bulb temp", AI, "temp", trend="Y", notes="Drives OA reset / economizer")
    add("OA-STN.RH", "Common", "OA-STN", "Outdoor-air station", "Rooftop", "Outdoor-air humidity", AI, "rh", trend="Y", notes="Wet-bulb/enthalpy computed in BMS")
    PANEL_HINT["POOL-FP"] = "LCP-B2"
    add("POOL-FP.SS", "Common", "POOL-FP", "Pool filtration pump", "Pool plant", "Start/Stop command", BO, "cmd", sp="Y", notes="Time schedule 8:00-19:00")
    add("POOL-FP.RUN", "Common", "POOL-FP", "Pool filtration pump", "Pool plant", "Run status", BI, "status")
    add("POOL-FP.TRIP", "Common", "POOL-FP", "Pool filtration pump", "Pool plant", "Fault", BI, "status", alarm="Y")

# --------------------------------------------------------------------------
# Build all points
# --------------------------------------------------------------------------
# Heat source
for i in (1, 2, 3):
    chiller_points(f"RC-1-{i}", "PH machine room")
for i in (1, 2, 3):
    PANEL_HINT[f"CP-8-{i}"] = "LCP-PH"
    vfd_pump_points(f"CP-8-{i}", "Primary CHW pump", "PH machine room", "Heat source",
                    notes_dp="Interlock w/ chiller; VFD")
for i in (1, 2, 3):
    cwpump_points(f"CWP-{i}", "PH / outdoor")
for i in (1, 2):
    tower_points(f"CT-{i}", "Rooftop")
hex_points("HEX-1", "Outdoor / PH")
# Secondary distribution + hot-water pumps (INFERRED)
for i in (1, 2, 3):
    PANEL_HINT[f"SCHWP-{i}"] = "LCP-PH"
    vfd_pump_points(f"SCHWP-{i}", "Secondary CHW distribution pump", "PH machine room",
                    "Heat source", notes_dp="INFERRED; DP-reset from most-open valve")
for i in (1, 2):
    PANEL_HINT[f"HWP-{i}"] = "LCP-B2"
    vfd_pump_points(f"HWP-{i}", "Hot-water pump (steam-HEX loop)", "B2F machine room",
                    "Heat source", notes_dp="INFERRED; heating loop off steam HEX")

# DHC steam interfaces
steam_points("DHC-STEAM-L", "B2F low-rise steam main", "low")
steam_points("DHC-STEAM-H", "Rooftop/PH high-rise steam main", "high")

# Air side
for n in range(1, 28):
    ahu_points(n)
for n in range(1, 16):
    evu_points(n)
for tag, area, panel in FCU:
    fcu_points(tag, area, panel)

# Ventilation fans
for tag, parent, inv in FANS:
    fan_points(tag, parent, inv)

# Metering + common
meter_points()
common_points()

# --------------------------------------------------------------------------
# Assign controllers (group devices per panel into DDCs of ~4 devices)
# --------------------------------------------------------------------------
# order devices by panel then first appearance
from collections import OrderedDict, defaultdict
panel_devices = OrderedDict()
for r in rows:
    r["Panel"] = r["Panel"] or PANEL_HINT.get(r["Device ID"], "LCP-PH")
    panel_devices.setdefault(r["Panel"], [])
    if r["Device ID"] not in panel_devices[r["Panel"]]:
        panel_devices[r["Panel"]].append(r["Device ID"])

def dev_category(d: str) -> str:
    """Class used to keep unlike equipment off the same DDC controller."""
    if d.startswith("RC-1"): return "chiller"
    if d.startswith("CP-8"): return "pchwp"
    if d.startswith("CWP-"): return "cwp"
    if d.startswith("CT-"): return "tower"
    if d.startswith("HEX-"): return "hex"
    if d.startswith("SCHWP-"): return "schwp"
    if d.startswith("HWP-"): return "hwp"
    if d.startswith("DHC-STEAM"): return "steam"
    if d.startswith("MTR-"): return "meter"
    if d.startswith("POOL"): return "pool"
    if d.startswith("OA-STN"): return "oa"
    if d.startswith("AC-"): return "ahu"
    if d.startswith("EVU-"): return "oau"
    if d.startswith("FCU-"): return "fcu"
    return "fan"   # EF/SF/RF

# Order categories so controllers list reads plant -> DHC -> air -> vent -> meters
CAT_ORDER = ["chiller", "pchwp", "cwp", "tower", "hex", "schwp", "hwp",
             "steam", "ahu", "oau", "fcu", "fan", "pool", "oa", "meter"]

dev_controller = {}
controllers = []   # (ctrl_id, panel, devices)
for panel, devs in panel_devices.items():
    by_cat = OrderedDict()
    for d in devs:
        by_cat.setdefault(dev_category(d), []).append(d)
    pshort = panel.replace("LCP-", "").replace("BMS-", "")
    idx = 1
    for cat in CAT_ORDER:
        clist = by_cat.get(cat, [])
        # chunk same-category devices by 3 into one controller
        for i in range(0, len(clist), 3):
            chunk = clist[i:i + 3]
            cid = f"DDC-{pshort}-{idx:02d}"
            for d in chunk:
                dev_controller[d] = cid
            controllers.append([cid, panel, ", ".join(chunk)])
            idx += 1

for r in rows:
    r["Controller"] = dev_controller.get(r["Device ID"], "")

# --------------------------------------------------------------------------
# Write workbook
# --------------------------------------------------------------------------
wb = Workbook()
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(bold=True, size=14, color="1F3864")
SUB_FONT = Font(italic=True, size=10, color="555555")
thin = Side(style="thin", color="D9D9D9")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
SYS_FILL = {
    "Heat source": "FCE4D6", "DHC interface": "FFF2CC", "Air side": "E2EFDA",
    "Ventilation": "DEEBF7", "Metering": "EDEDED", "Common": "F2F2F2",
}

def style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HDR_FILL; cell.font = HDR_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER

def set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

# ---- Cover ----
ws = wb.active
ws.title = "Cover"
ws["A1"] = "Red5-DHCP — BMS I/O List & Panel / Controller Schedule"
ws["A1"].font = TITLE_FONT
ws["A2"] = "ANA InterContinental Tokyo — District Heating & Cooling (DHC) connected hotel BMS"
ws["A2"].font = SUB_FONT
cover = [
    ("", ""),
    ("Building", "SRC, B3–37F, ~98,331 m²; Azbil (savic-net) BMS"),
    ("Energy source", "District Heating & Cooling (steam low-rise @B2F + high-rise @rooftop) + local water-cooled chillers"),
    ("Local plant", "RC-1 chillers ×3 (370 kW, COP 4.51), CP-8 primary CHW pumps ×3, HEX-1 plate HX (395 kW), cooling towers, condenser pumps"),
    ("Air side", "AC-1..27 AHUs (public/kitchen), EVU-1..15 outdoor-air units (guest-room/function zones), FCUs (36/37F 4-pipe), EF/SF/RF fans"),
    ("ESCO control scope", "Pump optimization, outdoor-air-unit optimization, thermal-demand control (per 共-01 spec)"),
    ("", ""),
    ("Sheets", "Panels · Controllers · IO_List · IO_Summary · Legend"),
    ("Basis", "As-built M-01 equipment schedule, 共-01 ESCO spec, 空調機スケジュール_20251127.xlsx"),
    ("Note", "Items marked 'INFERRED' (secondary/HW pumps, FCU quantity) must be confirmed against as-builts / Azbil 納入仕様書."),
]
r = 4
for k, v in cover:
    ws.cell(row=r, column=1, value=k).font = Font(bold=True, size=10)
    ws.cell(row=r, column=2, value=v).alignment = Alignment(wrap_text=True, vertical="top")
    r += 1
set_widths(ws, [22, 110])
for rr in range(5, r):
    ws.row_dimensions[rr].height = 30

# ---- Panels ----
ws = wb.create_sheet("Panels")
pcols = ["Panel ID", "Description", "Location", "Areas / Systems served",
         "Controllers", "I/O points"]
ws.append(pcols)
pt_by_panel = defaultdict(int)
for rr in rows:
    pt_by_panel[rr["Panel"]] += 1
ctrl_by_panel = defaultdict(int)
for cid, panel, devs in controllers:
    ctrl_by_panel[panel] += 1
for pid, desc, loc, served in PANELS:
    ws.append([pid, desc, loc, served, ctrl_by_panel.get(pid, 0), pt_by_panel.get(pid, 0)])
style_header(ws, len(pcols))
set_widths(ws, [14, 34, 26, 60, 12, 11])
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(pcols))}{ws.max_row}"
for rr in range(2, ws.max_row + 1):
    for c in range(1, len(pcols) + 1):
        ws.cell(row=rr, column=c).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=rr, column=c).border = BORDER

# ---- Controllers ----
ws = wb.create_sheet("Controllers")
ccols = ["Controller ID", "Panel", "Type", "Devices served", "Point count"]
ws.append(ccols)
pts_by_ctrl = defaultdict(int)
for rr in rows:
    pts_by_ctrl[rr["Controller"]] += 1
for cid, panel, devs in controllers:
    ws.append([cid, panel, "DDC field controller (Azbil Infilex/savic-net class)",
               devs, pts_by_ctrl.get(cid, 0)])
style_header(ws, len(ccols))
set_widths(ws, [16, 12, 42, 60, 12])
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(ccols))}{ws.max_row}"
for rr in range(2, ws.max_row + 1):
    for c in range(1, len(ccols) + 1):
        ws.cell(row=rr, column=c).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=rr, column=c).border = BORDER

# ---- IO_List ----
ws = wb.create_sheet("IO_List")
cols = ["Point Tag", "System", "Device ID", "Device Type", "Area / Served",
        "Panel", "Controller", "Point Description", "I/O Type",
        "Signal / Range", "Units", "SP/Sched", "Alarm", "Trend", "Notes / Basis"]
ws.append(cols)
for rr in rows:
    ws.append([rr[c] for c in cols])
style_header(ws, len(cols))
set_widths(ws, [16, 13, 12, 24, 34, 10, 13, 34, 8, 15, 8, 8, 7, 7, 46])
ws.freeze_panes = "C2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws.max_row}"
# system color banding + borders
for rr in range(2, ws.max_row + 1):
    sysname = ws.cell(row=rr, column=2).value
    fill = SYS_FILL.get(sysname)
    for c in range(1, len(cols) + 1):
        cell = ws.cell(row=rr, column=c)
        cell.border = BORDER
        cell.alignment = Alignment(wrap_text=True, vertical="top", size=9) if False else Alignment(wrap_text=True, vertical="top")
        cell.font = Font(size=9)
        if fill:
            cell.fill = PatternFill("solid", fgColor=fill)

# ---- IO_Summary ----
ws = wb.create_sheet("IO_Summary")
systems = ["Heat source", "DHC interface", "Air side", "Ventilation", "Metering", "Common"]
counts = {s: {"AI": 0, "AO": 0, "BI": 0, "BO": 0} for s in systems}
for rr in rows:
    counts.setdefault(rr["System"], {"AI": 0, "AO": 0, "BI": 0, "BO": 0})
    counts[rr["System"]][rr["I/O Type"]] += 1
scols = ["System", "AI", "AO", "BI", "BO", "Total"]
ws.append(scols)
tot = {"AI": 0, "AO": 0, "BI": 0, "BO": 0}
for s in systems:
    c = counts[s]
    row_total = sum(c.values())
    ws.append([s, c["AI"], c["AO"], c["BI"], c["BO"], row_total])
    for k in tot:
        tot[k] += c[k]
ws.append(["GRAND TOTAL", tot["AI"], tot["AO"], tot["BI"], tot["BO"], sum(tot.values())])
style_header(ws, len(scols))
set_widths(ws, [18, 8, 8, 8, 8, 10])
last = ws.max_row
for c in range(1, len(scols) + 1):
    ws.cell(row=last, column=c).font = Font(bold=True)
    ws.cell(row=last, column=c).fill = PatternFill("solid", fgColor="D6DCE4")
for rr in range(2, ws.max_row + 1):
    for c in range(1, len(scols) + 1):
        ws.cell(row=rr, column=c).border = BORDER
# device + point tallies
ws.cell(row=last + 2, column=1, value="Devices").font = Font(bold=True)
ws.cell(row=last + 2, column=2, value=len({r['Device ID'] for r in rows}))
ws.cell(row=last + 3, column=1, value="Panels").font = Font(bold=True)
ws.cell(row=last + 3, column=2, value=len(PANELS))
ws.cell(row=last + 4, column=1, value="Controllers").font = Font(bold=True)
ws.cell(row=last + 4, column=2, value=len(controllers))
ws.cell(row=last + 5, column=1, value="Total I/O points").font = Font(bold=True)
ws.cell(row=last + 5, column=2, value=len(rows))

# ---- Legend ----
ws = wb.create_sheet("Legend")
legend = [
    ("Abbreviation", "Meaning"),
    ("AI", "Analog Input (sensor: temperature, humidity, pressure, flow, power, position fb)"),
    ("AO", "Analog Output (modulating command: valve %, damper %, VFD speed %)"),
    ("BI", "Binary Input (status / fault / proof dry contact)"),
    ("BO", "Binary Output (start/stop / open-close relay)"),
    ("SP/Sched", "Point carries a setpoint or time/seasonal/event schedule"),
    ("CHW / CW", "Chilled water / Condenser water"),
    ("SAT / RAT", "Supply-air temp / Return-air temp"),
    ("CCV / HCV", "Cooling-coil valve / Heating-coil (steam) valve"),
    ("INV", "Inverter / VFD fan speed control"),
    ("Zero-energy band", "Deadband between heating & cooling to prevent simultaneous operation"),
    ("DHC", "District Heating & Cooling (external steam / chilled supply)"),
    ("HEX", "Plate heat exchanger (DHC / secondary-loop hydraulic separator)"),
    ("OAU (EVU)", "Outdoor-air / make-up-air unit"),
    ("INFERRED", "Not explicitly confirmed in supplied docs — verify vs as-builts / Azbil 納入仕様書"),
]
for row in legend:
    ws.append(row)
style_header(ws, 2)
set_widths(ws, [22, 95])
for rr in range(2, ws.max_row + 1):
    ws.cell(row=rr, column=1).font = Font(bold=True, size=10)
    ws.cell(row=rr, column=2).alignment = Alignment(wrap_text=True, vertical="top")
    for c in (1, 2):
        ws.cell(row=rr, column=c).border = BORDER

wb.save(OUT)
print("wrote", OUT)
print("total I/O points:", len(rows))
print("devices:", len({r['Device ID'] for r in rows}),
      "| panels:", len(PANELS), "| controllers:", len(controllers))
