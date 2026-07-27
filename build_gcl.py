"""build_gcl.py -- emit Delta Controls GCL+ control programs per controller.

Reuses the control-logic model (build_control_logic.build_model) and turns each
controller's Sequence of Operations into a GCL+ Program (PG) object listing.
BACnet objects are referenced by their point-tag name in quotes (e.g. "R-1.SS"),
which maps 1:1 to the I/O list, so a site engineer can bind them directly.

Syntax note (verify against your enteliWEB pg_reference.html):
  - Comments use a leading apostrophe  '
  - Blocks: If <cond> Then / Else / EndIf ; While <cond> / EndWhile
  - Binary present-values written as On / Off (Active/Inactive) ; analog = number
  - Setpoints / internal state held in AV/BV objects (names in quotes)
  - Reset/loops shown as GCL math; a native LOOP (PID) object may be used instead
Outputs:
  docs/gcl_programs.md               fenced GCL+ per controller
  exports/red5-dhcp_gcl-programs.gcl one combined listing (all programs)
  exports/red5-dhcp_gcl-programs.html interactive: search / copy / print
"""
from __future__ import annotations

import datetime
import html
import os

import build_control_logic as bcl

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(HERE, "exports")
DOCS_DIR = os.path.join(HERE, "docs")
TODAY = datetime.date.today().isoformat()


def sufmap(ctrl):
    """dev -> {SUFFIX: io_type} for every point on the controller."""
    m = {}
    for pt in ctrl["points"]:
        tag = pt["tag"]
        dev, suf = (tag.split(".", 1) + [""])[:2] if "." in tag else (tag, "")
        m.setdefault(dev, {})[suf.upper()] = pt["io"]
    return m


def T(dev, suf):
    return f'"{dev}.{suf}"'


def has(m, dev, suf):
    return suf in m.get(dev, {})


# ---------------------------------------------------------------------------
# Per-class GCL+ emitters -> list[str] lines
# ---------------------------------------------------------------------------
def e_chiller(devs, m):
    d = devs[0]
    L = ["' --- R-1 economic dispatch (DHC is default source) ---",
         "'  AVs: \"DHC Cost\" \"R1 Cost\" \"Loop PLR\" \"Most Open Valve\" \"Wetbulb\"",
         'If ("DHC Available" = Off) Or ("DHC Cost" > "R1 Cost" * 1.05) Then',
         '  If "Loop PLR" > 0.15 Then "R-1 Enable" = On',
         "Else",
         '  "R-1 Enable" = Off',
         "EndIf",
         "",
         "' --- CHW reset (trim & respond 7..10 C) and condenser reset (wetbulb+3.5, floor 19) ---",
         '"R-1 CHW SP" = Max(7, Min(10, 10 - ("Most Open Valve" - 90) / 10))',
         '"CW SP"     = Max(19, "Wetbulb" + 3.5)',
         "",
         "' --- Flow-proof interlock before enabling the machine ---",
         f'If ("CP-7.RUN" = Off) Or ("CDP-3.RUN" = Off) Then "R-1 Enable" = Off']
    if has(m, d, "SS"):
        L += ["", 'If "R-1 Enable" = On Then',
              f"  {T(d,'SS')} = On"]
        if has(m, d, "DMD"):
            L.append(f"  {T(d,'DMD')} = \"Capacity Limit\"")
        L += ["Else", f"  {T(d,'SS')} = Off", "EndIf"]
    if has(m, d, "TRIP"):
        L += ["", f"If {T(d,'TRIP')} = Active Then \"R-1 Alarm\" = On"]
    return L


def e_dhc_chw(devs, m):
    d = devs[0]
    L = ["' --- DHC chilled-water intake: modulate valve to hold CHW supply SP ---"]
    if has(m, d, "CV"):
        L += [f'{T(d,"CV")} = PID("CHW SP", {T(d,"CS-T")}, "CHW Loop")',
              "'  (or native LOOP object; direct-acting, output 0..100%)",
              "' Cap valve during district coincident-peak window",
              'If ("DHC Peak" = On) And ("Loop PLR" > 0.5) Then',
              f'  {T(d,"CV")} = Min({T(d,"CV")}, "Peak Valve Limit")',
              "EndIf"]
    if has(m, d, "CS-T"):
        L += ["", "' Alarms & fail-safe",
              f'If {T(d,"CS-T")} > "CHW Hi Limit" Then "DHC CHW Alarm" = On',
              f'If "BMS Comms" = Off Then {T(d,"CV")} = 100   \' fail-open to cooling']
    return L


def e_dhc_steam(devs, m):
    d = devs[0]
    return ["' --- DHC steam intake: PRV to 0.2 MPa house header, heating season only ---",
            'If "Heating Season" = On Then',
            f'  {T(d,"PRV") if has(m,d,"PRV") else chr(34)+d+".CV"+chr(34)} = PID("Steam Header SP", "House Steam P", "Steam PRV")',
            "Else",
            f'  {T(d,"PRV") if has(m,d,"PRV") else chr(34)+d+".CV"+chr(34)} = 0   \' isolate + drain',
            "EndIf",
            "' Meter mass flow + condensate hot-return for demand/energy"]


def e_tower(devs, m):
    cells = [d for d in devs if d.count("-") >= 2]
    L = ["' --- Cooling tower: INV fan cells hold condenser-water SP (wetbulb reset) ---",
         '"CW SP" = Max(19, "Wetbulb" + "CT Approach")']
    for c in cells:
        if has(m, c, "SPD"):
            L.append(f'{T(c,"SPD")} = PID("CW SP", "CW Return Temp", "Tower Loop")')
    if cells:
        lead = cells[0]
        L += ["", "' Stage additional cells as load rises (lead runs first)",
              f'If "CW Return Temp" > ("CW SP" + 1.5) Then {T(cells[-1],"SS")} = On',
              f'If "CW Return Temp" < ("CW SP" + 0.3) Then {T(cells[-1],"SS")} = Off',
              f'{T(lead,"SS")} = "Tower Enable"']
        L += ["", "' Freeze protection + fault", 
              'If "OA Temp" < 2 Then "CT Basin Heater" = On']
        for c in cells:
            if has(m, c, "TRIP"):
                L.append(f'If {T(c,"TRIP")} = Active Then "CT Alarm" = On')
    return L


def e_pump(devs, m, what):
    L = [f"' --- {what}: stage on demand, lead/lag/standby, VFD to header Dp ---"]
    lead = devs[0]
    L.append(f'{T(lead,"SS")} = "Loop Enable"')
    if len(devs) > 1:
        L += ["' Rotate lead on equal run-hours; stage lag on low Dp / high demand",
              f'If "Loop Dp" < ("Dp SP" - "Dp Db") Then {T(devs[1],"SS")} = On',
              f'If "Loop Dp" > ("Dp SP" + "Dp Db") Then {T(devs[-1],"SS")} = Off']
    for d in devs:
        if has(m, d, "SPD"):
            L.append(f'{T(d,"SPD")} = PID("Dp SP", "Loop Dp", "{what} Loop")')
    for d in devs:
        if has(m, d, "TRIP"):
            L.append(f'If {T(d,"TRIP")} = Active Then "{d} Alarm" = On')
    L.append("' Guarantee duty OR standby availability at all times")
    return L


def e_hx(devs, m, kind="tempered loop"):
    L = [f"' --- Heat exchanger ({kind}): primary valve holds secondary outlet SP ---"]
    for d in devs:
        if has(m, d, "PV") and has(m, d, "S-OUT"):
            L.append(f'{T(d,"PV")} = PID("{d} Sec SP", {T(d,"S-OUT")}, "{d} Loop")')
            L.append(f'If {T(d,"S-OUT")} > "{d} Hi Limit" Then "{d} Alarm" = On')
    return L


def e_freecool(devs, m):
    d = devs[0]
    return ["' --- Winter/shoulder free-cooling via tower + HX ---",
            'If ("Wetbulb" + "CT Approach") < ("CHW SP" - 1) Then',
            '  "Freecool Enable" = On',
            "Else",
            '  "Freecool Enable" = Off   \' hand back to mechanical cooling (hysteresis)',
            "EndIf",
            (f'If "Freecool Enable" = On Then {T(d,"PV")} = PID("CHW SP", "Loop Temp", "Freecool")'
             if has(m, d, "PV") else "")]


def e_ahu(devs, m):
    L = []
    for d in devs:
        L.append(f"' --- AHU {d}: schedule start, SAT control, economizer ---")
        if has(m, d, "SS"):
            L.append(f'{T(d,"SS")} = "Occupancy Sched"')
        if has(m, d, "SPDFB") and has(m, d, "SPD"):
            L.append(f'{T(d,"SPD")} = PID("Duct Static SP", "Duct Static", "{d} Fan")')
        elif has(m, d, "SPD"):
            L.append(f'{T(d,"SPD")} = "{d} Fan Speed"   \' constant volume')
        if has(m, d, "CCV") and has(m, d, "SAT"):
            L.append(f'{T(d,"CCV")} = PID("{d} SAT SP", {T(d,"SAT")}, "{d} Cool")')
        if has(m, d, "HCV"):
            L.append(f'{T(d,"HCV")} = PID_Heat("{d} SAT SP", {T(d,"SAT")}, "{d} Heat")  \' deadband vs cooling')
        if has(m, d, "OAD") or has(m, d, "CCV"):
            L.append("' Apr-May economizer: 100% OA free-cooling, cooling coil closed")
            L.append('If "Economizer OK" = On Then')
            if has(m, d, "OAD"):
                L.append(f'  {T(d,"OAD")} = 100')
            if has(m, d, "CCV"):
                L.append(f'  {T(d,"CCV")} = 0')
            L.append("EndIf")
        if has(m, d, "TRIP"):
            L.append(f'If {T(d,"TRIP")} = Active Then "{d} Fan Alarm" = On')
        if has(m, d, "SAT"):
            L.append(f'If "Freezestat" = Active Then {T(d,"SS")} = Off   \' freeze protection')
        L.append("")
    return L


def e_vent(devs, m):
    L = ["' --- Ventilation / exhaust: schedule + AHU/fire interlock ---"]
    for d in devs:
        if has(m, d, "SS"):
            L.append(f'{T(d,"SS")} = "Vent Sched" And ("Fire Mode" = Off)')
        if has(m, d, "TRIP"):
            L.append(f'If {T(d,"TRIP")} = Active Then "{d} Alarm" = On')
    return L


def e_packaged(devs, m):
    L = ["' --- Packaged DX: BMS enable/monitor; capacity on integral thermostat ---",
         "'  Electrical/IT-room units run 24/7 -> keep enabled"]
    for d in devs:
        if has(m, d, "SS"):
            L.append(f'{T(d,"SS")} = "{d} Enable"')
        if has(m, d, "TRIP"):
            L.append(f'If {T(d,"TRIP")} = Active Then "{d} Alarm" = On')
    return L


def e_lighting(devs, m):
    L = ["' --- Lighting groups: time / astronomical schedule ---"]
    for d in devs:
        if d.startswith("LTG-AVIATION"):
            L.append(f'{T(d,"CMD")} = "Photocell Dusk" Or "Aviation Always On"   \' life-safety, never dark')
        elif has(m, d, "CMD"):
            L.append(f'{T(d,"CMD")} = "{d} Sched"')
        if has(m, d, "ST"):
            L.append(f'If ({T(d,"CMD")} = On) And ({T(d,"ST")} = Off) Then "{d} Fault" = On')
    return L


def e_lighting_wrap(devs, m):
    return e_lighting(devs, m)


def e_generic(devs, m):
    L = ["' --- Supervise: enable, prove status, alarm ---"]
    for d in devs:
        if has(m, d, "SS"):
            L.append(f'{T(d,"SS")} = "{d} Enable"')
        if has(m, d, "TRIP"):
            L.append(f'If {T(d,"TRIP")} = Active Then "{d} Alarm" = On')
    return L


EMIT = {
    "chiller": e_chiller, "dhc_chw": e_dhc_chw, "dhc_steam": e_dhc_steam, "tower": e_tower,
    "freecool": e_freecool, "hx": lambda d, m: e_hx(d, m),
    "emhx": lambda d, m: e_hx(d, m, "emergency DHC loop"),
    "ahu": e_ahu, "vent": e_vent, "oa_station": e_vent, "fcu": e_generic,
    "packaged": e_packaged, "lighting": e_lighting, "meter": lambda d, m: ["' Energy meter -- monitor / integrate only (no output)."],
    "hotwell": e_generic, "expansion": e_generic, "changeover": e_generic, "generic": e_generic,
    "cond_pump": lambda d, m: e_pump(d, m, "Condenser pumps"),
    "chw_pump": lambda d, m: e_pump(d, m, "CHW pumps"),
    "hw_pump": lambda d, m: e_pump(d, m, "HW pumps"),
    "sec_pump": lambda d, m: e_pump(d, m, "Secondary pumps"),
    "hotwell_pump": lambda d, m: e_pump(d, m, "Hot-well pumps"),
}


def program_for(ctrl):
    m = sufmap(ctrl)
    L = ["'============================================================",
         f"' Program (PG): {ctrl['id']}   Panel: {ctrl['panel']}",
         f"' Equipment: {ctrl['devices']}",
         f"' Strategy : {ctrl['strategy']}",
         f"' I/O      : {ctrl['npoints']} pts (AI {ctrl['io']['AI']}  AO {ctrl['io']['AO']}"
         f"  BI {ctrl['io']['BI']}  BO {ctrl['io']['BO']})",
         "'  Objects referenced by point-tag name (see I/O list). Verify syntax",
         "'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).",
         "'============================================================", ""]
    for sec in ctrl["sections"]:
        if len(ctrl["sections"]) > 1:
            L.append(f"' === [{sec['label']}] {', '.join(sec['devices'])} ===")
        L += EMIT.get(sec["class"], e_generic)(sec["devices"], m)
        L.append("")
    L.append("End")
    return "\n".join(l for l in L)


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------
def render(m):
    programs = []  # (panel, ctrl, code)
    for p in m["panels"]:
        for c in p["controllers"]:
            programs.append((p, c, program_for(c)))

    # combined .gcl
    with open(os.path.join(EXPORT_DIR, "red5-dhcp_gcl-programs.gcl"), "w", encoding="utf-8") as f:
        f.write(f"' Red5-DHCP GCL+ control programs -- {len(programs)} controllers -- {TODAY}\n\n")
        for _p, _c, code in programs:
            f.write(code + "\n\n\n")

    # markdown
    with open(os.path.join(DOCS_DIR, "gcl_programs.md"), "w", encoding="utf-8") as f:
        f.write(f"# Red5-DHCP — GCL+ control programs\n\n")
        f.write(f"*Generated {TODAY} · {len(programs)} controllers. Delta Controls GCL+ "
                f"(vendor8). Objects referenced by point-tag name; verify syntax against your "
                f"enteliWEB `pg_reference.html`.*\n\n")
        cur = None
        for p, c, code in programs:
            if p["id"] != cur:
                cur = p["id"]
                f.write(f"\n## {p['id']} — {p['desc']}\n\n")
            f.write(f"### {c['id']}\n\n```gcl\n{code}\n```\n\n")

    # interactive HTML
    def esc(s):
        return html.escape(str(s))
    blocks = []
    cur = None
    for p, c, code in programs:
        blob = esc((c["id"] + " " + p["id"] + " " + c["devices"] + " " + c["strategy"]).lower())
        blocks.append(
            f'<details class="pg" data-s="{blob}"><summary>{esc(c["id"])}'
            f'<span class="r">{esc(p["id"])} · {esc(c["strategy"])}</span></summary>'
            f'<div class="eq">{esc(c["devices"])}</div>'
            f'<button class="cp" onclick="cp(this)">Copy</button>'
            f'<pre>{esc(code)}</pre></details>')
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Red5-DHCP — GCL+ programs</title>
<style>
 :root{{--ink:#1b2430;--dim:#5b6675;--line:#d5dbe4;--band:#1F3864;--code:#0d1117;--codeink:#d6dee8;}}
 *{{box-sizing:border-box}} body{{margin:0;font:13px/1.5 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:var(--ink);background:#f4f6f9;padding:24px}}
 .wrap{{max-width:1040px;margin:0 auto}} h1{{font-size:21px;margin:0 0 2px}} .sub{{color:var(--dim);margin:0 0 14px}}
 .bar{{position:sticky;top:0;background:#f4f6f9;padding:8px 0 12px;display:flex;gap:10px;flex-wrap:wrap;align-items:center;z-index:5}}
 input[type=search]{{border:1px solid var(--line);border-radius:7px;padding:7px 10px;min-width:300px;font-size:13px}}
 button{{border:1px solid var(--line);background:#fff;border-radius:7px;padding:6px 11px;cursor:pointer;font-size:12px}}
 details.pg{{background:#fff;border:1px solid var(--line);border-radius:9px;margin:0 0 8px;position:relative}}
 details.pg>summary{{padding:10px 14px;font-weight:600;cursor:pointer;list-style:none}}
 summary::-webkit-details-marker{{display:none}} summary .r{{float:right;color:var(--dim);font-weight:400;font-size:12px}}
 .eq{{color:var(--dim);font-size:12px;padding:0 14px 6px}}
 button.cp{{position:absolute;right:12px;top:40px}}
 pre{{background:var(--code);color:var(--codeink);margin:0;padding:14px 16px;border-radius:0 0 9px 9px;overflow:auto;
      font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre}}
 .hidden{{display:none!important}} .foot{{color:var(--dim);font-size:12px;margin-top:18px}}
 @media print{{body{{background:#fff;padding:0}} .bar,button.cp{{display:none}} details.pg{{break-inside:avoid}} pre{{background:#fff;color:#000;border:1px solid #ccc}}}}
</style></head><body><div class="wrap">
<h1>Red5-DHCP — GCL+ control programs (Delta Controls, vendor8)</h1>
<p class="sub">{len(programs)} controllers · generated {TODAY}. Objects referenced by point-tag name (I/O list). Verify comment token &amp; LOOP/PID against your enteliWEB pg_reference.html.</p>
<div class="bar">
 <input type="search" id="q" placeholder="find controller / equipment / strategy\u2026">
 <button id="expand">Expand all</button><button id="collapse">Collapse all</button>
 <button onclick="window.print()">Print / Save PDF</button><span class="sub" id="count"></span>
</div>
{"".join(blocks)}
<p class="foot">Source: build_gcl.py from the control-logic model. GCL+ syntax to confirm on site.</p>
</div>
<script>
const items=[...document.querySelectorAll('details.pg')];
const cnt=document.getElementById('count');cnt.textContent=items.length+' programs';
function cp(b){{const t=b.parentElement.querySelector('pre').innerText;navigator.clipboard.writeText(t);b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1200);}}
document.getElementById('q').addEventListener('input',e=>{{const s=e.target.value.trim().toLowerCase();let n=0;
 for(const d of items){{const hit=!s||d.dataset.s.includes(s);d.classList.toggle('hidden',!hit);if(hit)n++;d.open=!!s&&hit;}}
 cnt.textContent=n+' / '+items.length+' programs';}});
document.getElementById('expand').onclick=()=>items.forEach(d=>d.open=true);
document.getElementById('collapse').onclick=()=>items.forEach(d=>d.open=false);
</script></body></html>
"""
    with open(os.path.join(EXPORT_DIR, "red5-dhcp_gcl-programs.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    return len(programs)


if __name__ == "__main__":
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    model = bcl.build_model()
    n = render(model)
    print(f"GCL+ programs generated: {n} controllers")
