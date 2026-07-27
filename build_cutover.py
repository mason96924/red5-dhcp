"""build_cutover.py -- downloadable BMS controller-replacement cutover plan.

Mirrors the dhcp-controller-cutover-plan canvas into portable, print-friendly
files under exports/: HTML (opens in any browser, print-to-PDF), XLSX (Phases /
Playbook / Risks / Summary sheets) and CSV (phase table).
"""
from __future__ import annotations

import csv
import datetime
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(HERE, "exports")
TODAY = datetime.date.today().isoformat()

TITLE = "Red5-DHCP — BMS controller replacement: minimal-interruption cutover"
SUBTITLE = ("Migrate 84 Azbil savic-net FX2 field controllers across 11 panels to new DDC in the "
            "April–May shoulder season, using OA economizer free-cooling and local manual operation "
            "to keep the hotel conditioned throughout.")

STATS = [("Field controllers to replace", "84"), ("Field panels (+ head-end)", "11"),
         ("I/O points (commissioning checklist)", "1160"), ("Cutover window (Mar prep)", "Apr–May")]

WHY = ("Tokyo shoulder-season OA (~10–22 °C, low enthalpy) lets the airside economizer meet the load "
       "with no mechanical cooling, so the towers (LCP-CT) and R-1 chiller are already idle and swap "
       "cold. Heating is over, so hot-water hydronics are low-risk. DHC stays live as a warm-spell "
       "safety net and is migrated last.")
ENABLER = ("Each motor starter has a 手元/遠方 (local/remote) selector + DC24V ext start-stop + status "
           "feedback (confirmed on E-01/13-4). During a swap the equipment runs in LOCAL manual — fan "
           "hand-on, OA damper fixed ~100%, pump fixed-speed — independent of the BMS.")

# n, window, panels, state, method, risk
PHASES = [
    ("0", "March (hot)", "BMS-CENTRAL + network backbone", "n/a — runs in parallel",
     "Stand up new head-end alongside FX2; prefab panels; bench-test programs; point-verify vs I/O list", "Prep"),
    ("1", "early Apr", "LCP-CT (8) + R-1 / condenser loop in LCP-3637", "Idle — no mechanical cooling",
     "Power down & swap cold; recommission before any warm spell", "Low"),
    ("2", "April", "LCP-1F (3), 2F (4), 3F (4), 4F (7) + air-side of HSL/HSH/3637",
     "Economizer free-cooling carries load",
     "AHU→local, fan hand-on, OA damper ~100%; one AHU at a time; guest floors overnight", "Moderate"),
    ("3", "Apr–May", "LCP-HSL (17), LCP-HSH (11) — pumps / HX / hydronics", "Heating off; only trickle CHW needed",
     "One pump local fixed-speed / manual bypass; duty & standby never both down", "Moderate"),
    ("4", "May (last)", "LCP-DHC (7) — DHC chilled-water + steam intake", "Primary source; economizer covers building",
     "DHC valves/pumps to local manual + district coordination; low-occupancy weekend", "Critical"),
    ("A", "any time", "LCP-PKG (7) — IT / electrical-room packaged DX", "Runs 24/7 (not seasonal)",
     "DX to local thermostat; fast one-at-a-time; spare/portable cooling staged", "Critical"),
    ("B", "any time", "LCP-LTG (3) — common-area & facade lighting", "Runs to schedule",
     "Local switch/override; aviation obstruction light on independent circuit — never dark", "Moderate"),
]

PLAYBOOK = [
    ("AHU / OAU fans", "COS→手元, fan hand-ON, OA damper fixed ~100% (economizer), DHC coil valve left manually crackable",
     "Warm spell → be able to open the cooling valve within minutes"),
    ("CHW / HW pumps", "One pump hand-ON at fixed speed; DP/bypass set manually",
     "Keep duty OR standby always available; protect domestic-hot-water continuity"),
    ("Cooling towers / condenser / R-1", "Leave isolated & de-energised",
     "None — off-season; recommission before enabling mechanical cooling"),
    ("DHC intake", "Intake isolation + energy valves and pumps to local manual, fixed position",
     "Primary source — coordinate with district operator; do this phase last"),
    ("Packaged units (IT/elec rooms)", "DX on local thermostat, continuous run",
     "24/7 critical rooms — stage spare/portable cooling; swap one unit at a time"),
    ("Lighting", "Local switching / manual override per circuit",
     "Aviation obstruction light is regulatory life-safety — independent circuit, always lit"),
]

RISKS = [
    ("Cutover discipline", "warn",
     "Only one system in manual at any time. Guest-facing zones swapped overnight, back-of-house first. "
     "Old controller stays landed on a marshalling strip so you can revert to FX2 within minutes. "
     "Freeze all scope changes during the window; spares on site."),
    ("Never interrupt", "crit",
     "Life-safety interlocks — smoke control, stair pressurization, exhaust — remain live and coordinated "
     "with the fire-alarm system. Aviation obstruction light and IT/electrical-room cooling stay energised."),
    ("Verify every point", "info",
     "The 1,160-point I/O list is the master checklist. Per controller: point-to-point verify each "
     "AI/AO/BI/BO, functional-test, then trend 24–48 h before returning to auto."),
    ("Weather safety net", "ok",
     "DHC stays operational until Phase 4, so a warm spell is covered. The sequence guarantees the building "
     "always has either economizer free-cooling or the DHC source available."),
]

RISK_HEX = {"Prep": "E7ECF5", "Low": "DDF0E4", "Moderate": "FBEEDA", "Critical": "F7DEDE"}
RISK_HTML = {"Prep": "#eef2fb", "Low": "#e7f6ec", "Moderate": "#fdf2df", "Critical": "#fbe3e3"}
CALLOUT_HTML = {"warn": "#fdf2df", "crit": "#fbe3e3", "info": "#eef2fb", "ok": "#e7f6ec"}


# --- CSV -------------------------------------------------------------------
def write_csv(path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Phase", "Window", "Panels (controllers)", "Shoulder-season state",
                    "Swap method", "Risk"])
        w.writerows(PHASES)
        w.writerow([])
        w.writerow(["Manual-operation playbook"])
        w.writerow(["System", "Local-mode setup", "Watch-out"])
        w.writerows(PLAYBOOK)


# --- XLSX ------------------------------------------------------------------
def write_xlsx(path):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    HDR = PatternFill("solid", fgColor="1F3864")
    HF = Font(bold=True, color="FFFFFF", size=10)
    thin = Side(style="thin", color="D9D9D9")
    B = Border(left=thin, right=thin, top=thin, bottom=thin)

    def hdr(ws, n):
        for c in range(1, n + 1):
            ws.cell(row=1, column=c).fill = HDR
            ws.cell(row=1, column=c).font = HF

    def widths(ws, ws_w):
        for i, w in enumerate(ws_w, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

    def frame(ws, n):
        for rr in range(2, ws.max_row + 1):
            for c in range(1, n + 1):
                ws.cell(row=rr, column=c).border = B
                ws.cell(row=rr, column=c).alignment = Alignment(wrap_text=True, vertical="top")

    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append([TITLE]); ws.cell(row=1, column=1).font = Font(bold=True, size=14, color="1F3864")
    ws.append([SUBTITLE]); ws.cell(row=2, column=1).font = Font(italic=True, size=10, color="555555")
    ws.append([f"Generated {TODAY}"])
    ws.append([])
    for label, val in STATS:
        ws.append([label, val])
    ws.append([])
    ws.append(["Why April–May", WHY])
    ws.append(["Enabler — local/remote", ENABLER])
    widths(ws, [30, 90])
    for rr in range(1, ws.max_row + 1):
        ws.cell(row=rr, column=2).alignment = Alignment(wrap_text=True, vertical="top")

    ws = wb.create_sheet("Phases")
    ws.append(["Phase", "Window", "Panels (controllers)", "Shoulder-season state", "Swap method", "Risk"])
    hdr(ws, 6)
    for row in PHASES:
        ws.append(list(row))
        fill = RISK_HEX.get(row[5])
        if fill:
            for c in range(1, 7):
                ws.cell(row=ws.max_row, column=c).fill = PatternFill("solid", fgColor=fill)
    widths(ws, [7, 13, 40, 30, 46, 11])
    ws.freeze_panes = "A2"
    frame(ws, 6)

    ws = wb.create_sheet("Playbook")
    ws.append(["System", "Local-mode setup while BMS is disconnected", "Watch-out"])
    hdr(ws, 3)
    for row in PLAYBOOK:
        ws.append(list(row))
    widths(ws, [28, 60, 46])
    ws.freeze_panes = "A2"
    frame(ws, 3)

    ws = wb.create_sheet("Risks")
    ws.append(["Control", "Detail"])
    hdr(ws, 2)
    for title, _t, text in RISKS:
        ws.append([title, text])
    widths(ws, [24, 100])
    ws.freeze_panes = "A2"
    frame(ws, 2)

    wb.save(path)


# --- HTML (light, print-friendly) -----------------------------------------
def _rows_html():
    out = []
    for n, window, panels, state, method, risk in PHASES:
        out.append(
            f'<tr style="background:{RISK_HTML.get(risk, "#fff")}">'
            f"<td class=c>{html.escape(n)}</td><td>{html.escape(window)}</td>"
            f"<td>{html.escape(panels)}</td><td>{html.escape(state)}</td>"
            f"<td>{html.escape(method)}</td><td class=c><b>{html.escape(risk)}</b></td></tr>")
    return "".join(out)


def _play_html():
    return "".join(
        f"<tr><td><b>{html.escape(s)}</b></td><td>{html.escape(setup)}</td><td>{html.escape(w)}</td></tr>"
        for s, setup, w in PLAYBOOK)


def _risk_html():
    return "".join(
        f'<div class="call" style="background:{CALLOUT_HTML[t]}"><b>{html.escape(title)}</b>'
        f"<p>{html.escape(text)}</p></div>" for title, t, text in RISKS)


def write_html(path):
    stats = "".join(f'<div class="stat"><b>{v}</b><span>{html.escape(l)}</span></div>' for l, v in STATS)
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<style>
  :root {{ --ink:#1b2430; --dim:#5b6675; --line:#d8dee7; --band:#1F3864; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
          color:var(--ink); background:#f4f6f9; padding:28px; }}
  .page {{ max-width:1180px; margin:0 auto; background:#fff; border:1px solid var(--line);
           border-radius:10px; padding:28px 32px; }}
  h1 {{ font-size:22px; margin:0 0 4px; }} .sub {{ color:var(--dim); margin:0 0 18px; max-width:90ch; }}
  h2 {{ font-size:16px; margin:26px 0 8px; border-bottom:2px solid var(--band); padding-bottom:4px; color:var(--band); }}
  .stats {{ display:flex; gap:26px; flex-wrap:wrap; margin:0 0 16px; }}
  .stat b {{ font-size:22px; display:block; }} .stat span {{ color:var(--dim); font-size:12px; }}
  .cols {{ display:flex; gap:14px; flex-wrap:wrap; }}
  .call {{ flex:1; min-width:280px; border:1px solid var(--line); border-radius:8px; padding:12px 14px; }}
  .call b {{ display:block; margin-bottom:4px; }} .call p {{ margin:0; color:#33404f; font-size:13px; }}
  table {{ border-collapse:collapse; width:100%; margin:6px 0 6px; font-size:13px; }}
  th, td {{ border:1px solid var(--line); padding:7px 9px; text-align:left; vertical-align:top; }}
  thead th {{ background:var(--band); color:#fff; }} td.c, th.c {{ text-align:center; white-space:nowrap; }}
  .note {{ color:var(--dim); font-size:12px; margin:4px 0 0; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .foot {{ color:var(--dim); font-size:12px; margin-top:22px; }}
  @media print {{ body {{ background:#fff; padding:0; }} .page {{ border:0; }} }}
</style></head>
<body><div class="page">
<h1>{html.escape(TITLE)}</h1>
<p class="sub">{html.escape(SUBTITLE)}</p>
<div class="stats">{stats}</div>
<div class="cols">
  <div class="call" style="background:#e7f6ec"><b>Why April–May</b><p>{html.escape(WHY)}</p></div>
  <div class="call" style="background:#eef2fb"><b>The enabler: local/remote at every starter</b><p>{html.escape(ENABLER)}</p></div>
</div>
<h2>Phased sequence — coldest/idle first, primary source last</h2>
<p class="note">Row shading = comfort/continuity risk during that phase. One system in manual at a time; guest floors overnight.</p>
<table><thead><tr><th class=c>#</th><th>Window</th><th>Panels (controllers)</th><th>Shoulder-season state</th><th>Swap method</th><th class=c>Risk</th></tr></thead>
<tbody>{_rows_html()}</tbody></table>
<p class="note">Split panels (LCP-3637 / HSL / HSH mix air-side + heat-source controllers) are migrated across phases by sub-system, not all at once.</p>
<h2>Manual-operation playbook (during each controller's swap)</h2>
<table><thead><tr><th>System</th><th>Local-mode setup while BMS is disconnected</th><th>Watch-out</th></tr></thead>
<tbody>{_play_html()}</tbody></table>
<h2>Risk controls & rollback</h2>
<div class="grid2">{_risk_html()}</div>
<p class="foot">Generated {TODAY} · Red5-DHCP · savic-net FX2 → new DDC migration. Print to PDF for distribution.</p>
</div></body></html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


if __name__ == "__main__":
    os.makedirs(EXPORT_DIR, exist_ok=True)
    stem = os.path.join(EXPORT_DIR, "red5-dhcp_controller-cutover-plan")
    write_csv(stem + ".csv")
    write_xlsx(stem + ".xlsx")
    write_html(stem + ".html")
    print("cutover plan exported:", stem + ".{csv,xlsx,html}")
