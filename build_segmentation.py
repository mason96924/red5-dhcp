"""build_segmentation.py -- phase summary of one continuous project delivery.

The 2026-09-05 draft split this retrofit into four separately awarded segments.
That presentation is withdrawn. The same work is five overlapping phases of one
contract. Duration is nine months. Completion is the contract date plus nine months.

  Phase 1  fabrication       -- panels built and FAT'd in the factory
  Phase 2  device network    -- new cable; the installed Azbil trunk may be IEIEJ p-A
  Phase 3  installation      -- panels swapped, field points re-terminated
  Phase 4  instruments       -- analog sensors and actuators replaced
  Phase 5  programming       -- programs loaded, system tuned, handed over

DEJ is the prime contractor. TYBMS is subcontracted to DEJ. The phases overlap.
They are not separate contracts.

Quantities come from the AUTHORITATIVE physical panel schedule
(panels_schedule.json -- 판넬별 포인트 정리 26.07.30) and reconcile to the same
67 panels / 4,467 points as build_cutover.py and build_commissioning.py:

  S1  67 panels, 904 controllers + modules      (capacity 5,240 pts)
  S2  67 panels, 4,467 terminations             (DO/DI/BTOT/AI/AO)
  S3  591 analog devices                        (505 AI + 86 AO)
  S4  109 DDC programs, 4,467 functional tests  (1,383 characterised points)

Stage gates still use the commissioning checklist columns: factory acceptance,
Wired / Terminated, P2P verified, Func. test. Those columns mark progress
through the one delivery.

Outputs: exports/red5-dhcp_phase-plan.{csv,xlsx,html}
         docs/phase_plan.md
"""
from __future__ import annotations

import csv
import datetime
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(HERE, "exports")
DOCS_DIR = os.path.join(HERE, "docs")
SCHEDULE = os.path.join(HERE, "panels_schedule.json")
TODAY = datetime.date.today().isoformat()

# --- load physical schedule ------------------------------------------------
_sched = json.load(open(SCHEDULE, encoding="utf-8"))
_PANELS = _sched["panels"]
SRC = _sched.get("source", "")

N_PANELS = len(_PANELS)
N_POINTS = _sched["usedTotal"]
N_CAP = _sched["capTotal"]
N_MODULES = sum(_sched["modTotals"])
TYPES = _sched["typeTotals"]

N_AI = TYPES["AI"]
N_AO = TYPES["AO"]
N_BTOT = TYPES["BTOT"]
N_ANALOG = N_AI + N_AO          # the sensor/actuator replacement scope
N_BINARY = TYPES["DI"] + TYPES["DO"]

# Functional model (generate_io_list.py), used for the programming segment.
N_DDC = 109
N_FUNC_POINTS = 1383
N_DEVICES = 259

# Value ceiling per segment, from the 2026-09-03 meeting. See VERIFY -- the
# statutory test is not actually a headline contract value.
CAP_USD = 400_000

TITLE = "Red5-DHCP — continuous project delivery, by phase"
SUBTITLE = (
    f"One contract for the {N_PANELS}-panel / {N_POINTS:,}-point savic-netFX2 → Delta retrofit. "
    f"Five phases overlap across nine months. The completion date is the contract date plus nine months. "
    f"DEJ holds the contract. TYBMS is subcontracted to DEJ."
)

STATS = [
    ("Phases", "5, overlapping"),
    ("Duration", "9 months from the contract date"),
    ("Panels (Phase 1 build → Phase 3 install)", f"{N_PANELS}"),
    ("Controllers + modules (Phase 1)", f"{N_MODULES}"),
    ("Field terminations (Phase 3)", f"{N_POINTS:,}"),
    ("Analog devices (Phase 4)", f"{N_ANALOG}"),
    ("DDC programs (Phase 5)", f"{N_DDC}"),
]

RATIONALE = (
    "This is one continuous delivery. Fabrication, the new device network, installation, instruments and "
    "programming overlap inside the same nine months, under the one contract. The phases name the kind of work."
)
SEQUENCING = (
    "Phase 5 authoring starts in month C+1 so the factory can bench-load. Phase 2 proves each new "
    "network run before that wave's first panel. On site, installation, instruments and programming "
    "happen inside the same area wave, the same night. An area returns to automatic control only when "
    "its program is proved. The playbook covers one panel at a time."
)
INDEPENDENCE = (
    "The commissioning checklist still records progress: factory acceptance, Wired and Terminated, "
    "P2P verified, and Func. test. Those columns are stage gates of the one delivery. They are not "
    "separate completion contracts."
)

# --- the four segments -----------------------------------------------------
# (no, code, title, nature, licence question, window, objective,
#  scope[], deliverables[], acceptance[], depends_on, cap_risk)
SEGMENTS = [
    (
        "Phase 1", "FAB", "Panel fabrication, supply & factory acceptance",
        "Off-site manufacture / supply",
        "Likely NOT 建設業 (goods manufacture + supply) — confirm",
        "C+0 to C+6 mo",
        "Deliver every DDC panel to site already built, loaded and factory-tested, so that on-site time is "
        "reduced to swapping an enclosure and landing wires.",
        [
            f"Procure {N_MODULES} Delta controllers and I/O modules against the panel schedule",
            f"Build and wire {N_PANELS} enclosures to {N_CAP:,}-point capacity ({N_POINTS:,} used, "
            f"{N_CAP - N_POINTS:,} spare)",
            "Head-end hardware: replacement of the BMS / SMS / DSS server role and the two operator consoles",
            "Bench-load the GCL+ programs and simulate I/O at the factory",
            "Panel general-arrangement and termination drawings, spares schedule",
        ],
        [
            f"{N_PANELS} panels delivered to site, labelled per the panel schedule",
            "FAT certificate per panel (module count, addressing, power-up, simulated I/O)",
            "As-built panel drawings + terminal schedules",
            "Head-end hardware delivered and staged",
            "Spare-parts list and recommended holding",
        ],
        [
            f"Module count reconciles to {N_MODULES} against panels_schedule.json",
            "FAT witnessed and signed per panel; no panel ships on a failed FAT",
            "Delivery note signed at site — this is the transfer of title, no site work involved",
        ],
        "—",
        "Hands panels to Phase 3 in wave order. Bench-load needs the programs from Phase 5, which starts in month C+1.",
    ),
    (
        "Phase 2", "NET", "Device-network cabling",
        "New field network, inside the same contract",
        "Same licence question as the site electrical work — confirm",
        "C+0 survey · C+2 to C+6 install · proved before each wave",
        "Identify the installed Azbil cable and, where it is IEIEJ p-A or otherwise unsuitable, install a new "
        "device network before cutover. This phase does not add a month.",
        [
            "Survey panels and risers. The 2002 drawing names IPEV-S 0.9 mm². The installed cable may be IEIEJ p-A.",
            "Reuse a run only when a test shows it meets the new network specification. IEIEJ p-A is not assumed reusable.",
            "Design and pull the new risers and floor cabling while the old network is still in service",
            "Prove continuity, insulation and communications on each run before that wave starts",
            "Record abandoned cable so a later crew does not land a new panel on it",
        ],
        [
            "Cable identification record",
            "Reuse or replace decision per riser",
            "Network drawings and cable schedule",
            "Segment test certificate before each wave",
            "As-built network drawings",
        ],
        [
            "Cable type recorded before the network design is approved",
            "Each wave's new run tested before that wave's first panel is cut over",
            "IEIEJ p-A not landed on the new panels unless a test says the run meets the specification",
        ],
        "Starts with Phase 1, in the contract month",
        "Each cutover wave lands on a run this phase has already proved.",
    ),
    (
        "Phase 3", "INST", "Panel replacement & field termination",
        "Electrical installation (on-site construction)",
        "電気工事業 — almost certainly required",
        "C+5 mo mobilise · C+6 to C+8 mo by wave",
        "Physically replace the Azbil RS/RCP/CP panels with the new DDC panels and transfer every field "
        "termination, without the hotel losing conditioning.",
        [
            f"Remove {N_PANELS} existing Azbil RS/RCP/CP panels, install their replacements",
            f"Transfer and land {N_POINTS:,} field terminations "
            f"({N_BINARY:,} binary, {N_BTOT} pulse, {N_ANALOG} analog)",
            "Land each panel on the device-network run proved in Phase 2. Do not reuse IEIEJ p-A unless that test passed",
            "Panel power, earthing, containment and making good",
            "Old controller left landed on a marshalling strip for rollback",
        ],
        [
            f"{N_PANELS} panels installed and energised",
            "Per-panel wiring completion certificate",
            "Continuity / insulation test records",
            "Marked-up termination drawings (as-installed)",
            "Rollback arrangement demonstrated per area wave",
        ],
        [
            f'"Wired" and "Terminated" signed for all {N_POINTS:,} points on the commissioning checklist',
            "Insulation and continuity results within limits, per panel",
            "The panel is on the proved new run before the wave is closed",
        ],
        "Phase 1 panels for that wave, and the Phase 2 run for that wave",
        "The same night continues into instruments and programming.",
    ),
    (
        "Phase 4", "INSTR", "Field instrumentation replacement & calibration",
        "Instrumentation installation (on-site construction)",
        "管工事 / 電気 / 計装 — category to be confirmed",
        "C+6 to C+8 mo, inside each wave after the panel is energised",
        "Replace and calibrate the analog field devices so the new controllers read true values, which is "
        "what the optimisation sequences depend on.",
        [
            f"Replace {N_AI} analog input devices — temperature, humidity, pressure, flow, energy",
            f"Replace {N_AO} analog output devices — modulating valves and damper actuators",
            f"Verify (not replace) {N_BTOT} pulse / totalizer interfaces from existing meters",
            "Re-range and calibrate each loop against the I/O list engineering units",
            "Immersion wells, averaging elements and impulse lines made good",
        ],
        [
            f"{N_ANALOG} analog devices installed",
            "Calibration certificate per loop, traceable",
            "Loop schedules marked with as-installed range and units",
            f"{N_BTOT} pulse interfaces proven for count and scaling",
        ],
        [
            f'"P2P verified" signed for all {N_ANALOG} analog points',
            "Two-point calibration recorded for every AI; stroke test for every AO",
            "Reading agreement against a reference instrument within tolerance",
        ],
        "Phase 3 (panel live for that area)",
        "The same night continues into the functional test.",
    ),
    (
        "Phase 5", "ENG", "Programming, integration, tuning & handover",
        "Engineering / software services",
        "情報通信工事 — or arguably not 建設業 at all; confirm",
        "C+1 mo authoring · C+5 mo head-end · C+6 mo through completion",
        "Make the installed hardware behave: load the control logic, prove every point, tune the sequences "
        "and hand a working system to the hotel.",
        [
            f"Load and commission {N_DDC} DDC control programs (GCL+, one PG object per controller)",
            f"Build the head-end point database and graphics for {N_FUNC_POINTS:,} characterised points "
            f"across {N_DEVICES} devices",
            "R-1 chiller optimiser: economic dispatch, CW/CHW reset, staging, FDD",
            "Trend, alarm, time-program, calendar and reporting configuration",
            f"Functional test of all {N_POINTS:,} points; 24–48 h trend per panel before auto",
            "Seasonal tuning through first cooling season; operator training; O&M documentation",
        ],
        [
            f"{N_DDC} programs loaded and version-controlled",
            "Head-end graphics and database live on the new servers",
            "Functional test sheets, complete",
            "Trend evidence per panel",
            "Sequence-of-Operations compliance record against docs/control_logic.md",
            "Training delivered; as-built documentation issued",
        ],
        [
            f'"Func. test" signed for all {N_POINTS:,} points',
            "Each controller demonstrated against its SOO",
            "24–48 h stable trend per panel before hand-back to auto",
            "Operator sign-off after training",
        ],
        "Phase 3 and Phase 4 for that area wave. Authoring itself starts in month C+1.",
        "Closes the project at the contract date plus nine months.",
    ),
]

SEG_COLS = ["Phase", "Name", "Nature of work", "Licence question", "Window",
            "Objective", "Continues from", "How the delivery continues"]

# --- how the packages interleave with the existing cutover waves -----------
# Area waves are build_cutover.py's phases, so the two plans stay consistent.
WAVE_COLS = ["Wave", "Area", "Panels", "Points", "Phase 1 fabricate", "Phase 2 network",
             "Phase 3 install", "Phase 4 instruments", "Phase 5 program"]
WAVES = [
    ("0", "Central head-end (B2F 시스템 제어반)", 1, 25,
     "C+0–C+2", "proved before C+5", "C+5", "n/a", "C+5 — alongside FX2"),
    ("1", "Penthouse PH1/PH2 — rooftop plant, R-1, OAUs", 9, 710,
     "C+0–C+3", "proved before C+6", "C+6", "C+6", "C+6"),
    ("2", "Guest & public floors — 31F, 21F, 10F, 4F–1F", 26, 2083,
     "C+1–C+4", "proved before C+6", "C+6–C+7", "C+6–C+7", "C+6–C+7"),
    ("3", "Basements B1–B3 — plant, hydronics, DHC intake", 31, 1649,
     "C+2–C+5", "proved before C+6", "C+6–C+7, last", "C+6–C+7", "C+7–C+8"),
]
_WAVE_PAN = sum(w[2] for w in WAVES)
_WAVE_PTS = sum(w[3] for w in WAVES)

# --- quantity reconciliation ----------------------------------------------
QTY_COLS = ["Quantity", "Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5", "Basis"]
QUANTITIES = [
    ("Panels", f"{N_PANELS} built", "—", f"{N_PANELS} installed", "—", "—",
     "panels_schedule.json"),
    ("Controllers + modules", f"{N_MODULES}", "—", "—", "—", f"{N_DDC} programs",
     "modTotals / functional model"),
    ("Field points", f"{N_CAP:,} capacity", "—", f"{N_POINTS:,} terminated",
     f"{N_ANALOG} calibrated", f"{N_POINTS:,} function-tested", "usedTotal / typeTotals"),
    ("Device network", "—", "survey, new cable, proved per wave", "landed at cutover",
     "—", "comms proved", "installed cable may be IEIEJ p-A"),
    ("Analog devices", "—", "—", "—", f"{N_AI} AI + {N_AO} AO", "—", "typeTotals"),
    ("Pulse / totalizer", "—", "—", f"{N_BTOT} landed", f"{N_BTOT} verified", "—", "typeTotals"),
    ("Checklist column", "FAT record", "run proved", "Wired + Terminated", "P2P verified",
     "Func. test", "build_commissioning.py"),
]

# --- open items the plan cannot resolve on its own -------------------------
VERIFY = [
    ("Threshold basis", "crit",
     "特定建設業許可 is triggered by the value a prime contractor SUBCONTRACTS OUT "
     "(4,500万円, or 7,000万円 for 建築一式工事) — not by the headline contract value. If that is the "
     "operative test, then how much the prime subcontracts matters more than how the contract is divided. "
     "DEJ is the prime. TYBMS is subcontracted to DEJ, so the test is the value DEJ places with TYBMS and "
     "any other subcontractor. Confirm with counsel against that subcontract, not against a four-way split."),
    ("Licence category for BMS", "warn",
     "Whether BMS work is 電気工事, 管工事, 情報通信工事 or a combination is still unresolved. It decides "
     "which phases need a licence. Phase 1 is manufacture. Phase 5 is largely services. The site exposure "
     "sits in Phase 2, Phase 3 and Phase 4."),
    ("One delivery", "info",
     "The proposal is one continuous project under DEJ. It is not a four-segment split, and it is not "
     "four payment contracts. A split whose only purpose is a value cap is the arrangement this plan "
     "no longer presents."),
    ("Prime contractor identity", "info",
     "Furukawa Denki has backed out. DEJ submits the proposal and holds the main contract. TYBMS is "
     "subcontracted to DEJ."),
    ("Continuity of control", "crit",
     "Phases 3, 4 and 5 run inside the same area wave. If installation finished building-wide before "
     "programming started, the hotel would sit on manual control for months. The playbook supports one "
     "panel at a time."),
    ("Foreign personnel", "info",
     "Scope of work permitted for Korean crews, insurance liability and safety responsibility are "
     "unresolved in writing. They bear on the on-site phases, Phase 3 and Phase 4."),
]

CALLOUT_HTML = {"warn": "#fdf2df", "crit": "#fbe3e3", "info": "#eef2fb", "ok": "#e7f6ec"}
SEG_HTML = {"Phase 1": "#eef2fb", "Phase 2": "#e7f4f4", "Phase 3": "#e7f6ec",
            "Phase 4": "#fdf2df", "Phase 5": "#f3eefb"}
SEG_HEX = {"Phase 1": "E7ECF5", "Phase 2": "DCEEEE", "Phase 3": "DDF0E4",
           "Phase 4": "FBEEDA", "Phase 5": "EFE7FA"}


def _seg_rows():
    """Flatten SEGMENTS to the summary table row shape."""
    return [(no, title, nature, lic, window, objective, dep, cap)
            for no, _code, title, nature, lic, window, objective,
            _scope, _deliv, _acc, dep, cap in SEGMENTS]


# --- CSV -------------------------------------------------------------------
def write_csv(path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(SEG_COLS)
        w.writerows(_seg_rows())
        w.writerow([])
        w.writerow(["Scope, deliverables and acceptance"])
        w.writerow(["Phase", "Section", "Item"])
        for no, _c, _t, _n, _l, _w, _o, scope, deliv, acc, _d, _cap in SEGMENTS:
            for s in scope:
                w.writerow([no, "Scope", s])
            for s in deliv:
                w.writerow([no, "Deliverable", s])
            for s in acc:
                w.writerow([no, "Acceptance", s])
        w.writerow([])
        w.writerow(["Execution — phases overlap by cutover area wave"])
        w.writerow(WAVE_COLS)
        w.writerows(WAVES)
        w.writerow(["TOTAL", "", _WAVE_PAN, _WAVE_PTS, "", "", "", "", ""])
        w.writerow([])
        w.writerow(["Quantity reconciliation"])
        w.writerow(QTY_COLS)
        w.writerows(QUANTITIES)
        w.writerow([])
        w.writerow(["Open items requiring confirmation"])
        w.writerow(["Item", "Severity", "Detail"])
        w.writerows(VERIFY)


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
    ws.append([TITLE])
    ws.cell(row=1, column=1).font = Font(bold=True, size=14, color="1F3864")
    ws.append([SUBTITLE])
    ws.cell(row=2, column=1).font = Font(italic=True, size=10, color="555555")
    ws.append([f"Generated {TODAY}"])
    ws.append([])
    for label, val in STATS:
        ws.append([label, val])
    ws.append([])
    ws.append(["Continuous delivery", RATIONALE])
    ws.append(["How the phases overlap", SEQUENCING])
    ws.append(["Stage gates", INDEPENDENCE])
    widths(ws, [34, 96])
    for rr in range(1, ws.max_row + 1):
        ws.cell(row=rr, column=2).alignment = Alignment(wrap_text=True, vertical="top")

    ws = wb.create_sheet("Phases")
    ws.append(SEG_COLS)
    hdr(ws, len(SEG_COLS))
    for row in _seg_rows():
        ws.append(list(row))
        fill = SEG_HEX.get(row[0])
        if fill:
            for c in range(1, len(SEG_COLS) + 1):
                ws.cell(row=ws.max_row, column=c).fill = PatternFill("solid", fgColor=fill)
    widths(ws, [7, 38, 28, 30, 26, 56, 22, 44])
    ws.freeze_panes = "A2"
    frame(ws, len(SEG_COLS))

    ws = wb.create_sheet("Scope-Deliverables")
    ws.append(["Phase", "Name", "Section", "Item"])
    hdr(ws, 4)
    for no, _c, title, _n, _l, _w, _o, scope, deliv, acc, _d, _cap in SEGMENTS:
        for section, items in (("Scope", scope), ("Deliverable", deliv), ("Acceptance", acc)):
            for s in items:
                ws.append([no, title, section, s])
                fill = SEG_HEX.get(no)
                if fill:
                    for c in range(1, 5):
                        ws.cell(row=ws.max_row, column=c).fill = PatternFill("solid", fgColor=fill)
    widths(ws, [7, 38, 15, 92])
    ws.freeze_panes = "A2"
    frame(ws, 4)

    ws = wb.create_sheet("Execution")
    ws.append(WAVE_COLS)
    hdr(ws, len(WAVE_COLS))
    for row in WAVES:
        ws.append(list(row))
    ws.append(["TOTAL", "", _WAVE_PAN, _WAVE_PTS, "", "", "", "", ""])
    for c in range(1, len(WAVE_COLS) + 1):
        ws.cell(row=ws.max_row, column=c).font = Font(bold=True)
    widths(ws, [8, 46, 9, 9, 16, 20, 18, 18, 26])
    ws.freeze_panes = "A2"
    frame(ws, len(WAVE_COLS))

    ws = wb.create_sheet("Quantities")
    ws.append(QTY_COLS)
    hdr(ws, len(QTY_COLS))
    for row in QUANTITIES:
        ws.append(list(row))
    widths(ws, [22, 16, 32, 22, 22, 24, 28])
    ws.freeze_panes = "A2"
    frame(ws, len(QTY_COLS))

    ws = wb.create_sheet("Open items")
    ws.append(["Item", "Severity", "Detail"])
    hdr(ws, 3)
    for row in VERIFY:
        ws.append(list(row))
    widths(ws, [26, 11, 110])
    ws.freeze_panes = "A2"
    frame(ws, 3)

    wb.save(path)


# --- HTML (light, print-friendly; same house style as the cutover plan) ----
def _seg_table_html():
    out = []
    for no, title, nature, lic, window, objective, dep, cap in _seg_rows():
        out.append(
            f'<tr style="background:{SEG_HTML.get(no, "#fff")}">'
            f"<td class=c><b>{html.escape(no)}</b></td><td><b>{html.escape(title)}</b></td>"
            f"<td>{html.escape(nature)}</td><td>{html.escape(lic)}</td>"
            f"<td>{html.escape(window)}</td><td>{html.escape(objective)}</td>"
            f"<td>{html.escape(dep)}</td><td>{html.escape(cap)}</td></tr>")
    return "".join(out)


def _detail_html():
    out = []
    for no, _c, title, nature, _l, window, objective, scope, deliv, acc, dep, _cap in SEGMENTS:
        def ul(items):
            return "".join(f"<li>{html.escape(i)}</li>" for i in items)
        out.append(
            f'<div class="seg" style="border-left:6px solid #1F3864; background:{SEG_HTML.get(no)}">'
            f"<h3>{html.escape(no)} — {html.escape(title)}</h3>"
            f'<p class="meta">{html.escape(nature)} · {html.escape(window)} · '
            f"depends on {html.escape(dep)}</p>"
            f"<p><b>Objective.</b> {html.escape(objective)}</p>"
            f'<div class="grid3">'
            f"<div><b>Scope</b><ul>{ul(scope)}</ul></div>"
            f"<div><b>Deliverables</b><ul>{ul(deliv)}</ul></div>"
            f"<div><b>Acceptance / completion</b><ul>{ul(acc)}</ul></div>"
            f"</div></div>")
    return "".join(out)


def _wave_html():
    rows = "".join(
        "<tr><td class=c>" + html.escape(w[0]) + "</td><td>" + html.escape(w[1]) + "</td>"
        f"<td class=c>{w[2]}</td><td class=c>{w[3]:,}</td>"
        + "".join(f"<td class=c>{html.escape(x)}</td>" for x in w[4:]) + "</tr>"
        for w in WAVES)
    rows += (f'<tr style="font-weight:700"><td></td><td>TOTAL</td><td class=c>{_WAVE_PAN}</td>'
             f'<td class=c>{_WAVE_PTS:,}</td><td></td><td></td><td></td><td></td><td></td></tr>')
    return rows


def _qty_html():
    return "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>"
        for row in QUANTITIES)


def _verify_html():
    return "".join(
        f'<div class="call" style="background:{CALLOUT_HTML[t]}"><b>{html.escape(title)}</b>'
        f"<p>{html.escape(text)}</p></div>" for title, t, text in VERIFY)


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
  h1 {{ font-size:22px; margin:0 0 4px; }} .sub {{ color:var(--dim); margin:0 0 18px; max-width:95ch; }}
  h2 {{ font-size:16px; margin:26px 0 8px; border-bottom:2px solid var(--band); padding-bottom:4px; color:var(--band); }}
  h3 {{ font-size:15px; margin:0 0 2px; }}
  .stats {{ display:flex; gap:26px; flex-wrap:wrap; margin:0 0 16px; }}
  .stat b {{ font-size:22px; display:block; }} .stat span {{ color:var(--dim); font-size:12px; }}
  .cols {{ display:flex; gap:14px; flex-wrap:wrap; }}
  .call {{ flex:1; min-width:280px; border:1px solid var(--line); border-radius:8px; padding:12px 14px; }}
  .call b {{ display:block; margin-bottom:4px; }} .call p {{ margin:0; color:#33404f; font-size:13px; }}
  table {{ border-collapse:collapse; width:100%; margin:6px 0; font-size:13px; }}
  th, td {{ border:1px solid var(--line); padding:7px 9px; text-align:left; vertical-align:top; }}
  thead th {{ background:var(--band); color:#fff; }} td.c, th.c {{ text-align:center; white-space:nowrap; }}
  .note {{ color:var(--dim); font-size:12px; margin:4px 0 0; }}
  .seg {{ border:1px solid var(--line); border-radius:8px; padding:14px 16px; margin:12px 0; }}
  .seg .meta {{ color:var(--dim); font-size:12px; margin:0 0 8px; }}
  .grid3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; }}
  .grid3 ul {{ margin:4px 0 0; padding-left:18px; }} .grid3 li {{ font-size:13px; margin-bottom:3px; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .foot {{ color:var(--dim); font-size:12px; margin-top:22px; }}
  @media print {{ body {{ background:#fff; padding:0; }} .page {{ border:0; }} .seg {{ break-inside:avoid; }} }}
  @media (max-width:900px) {{ .grid3, .grid2 {{ grid-template-columns:1fr; }} }}
</style></head>
<body><div class="page">
<h1>{html.escape(TITLE)}</h1>
<p class="sub">{html.escape(SUBTITLE)}</p>
<div class="stats">{stats}</div>
<div class="cols">
  <div class="call" style="background:#e7f6ec"><b>One continuous delivery</b><p>{html.escape(RATIONALE)}</p></div>
  <div class="call" style="background:#fdf2df"><b>The phases overlap</b><p>{html.escape(SEQUENCING)}</p></div>
  <div class="call" style="background:#eef2fb"><b>Stage gates, not separate contracts</b><p>{html.escape(INDEPENDENCE)}</p></div>
</div>
<h2>The five phases</h2>
<table><thead><tr>{"".join(f'<th{" class=c" if c == "Phase" else ""}>{html.escape(c)}</th>' for c in SEG_COLS)}</tr></thead>
<tbody>{_seg_table_html()}</tbody></table>
<p class="note">The phases overlap. The right-hand column says how each one hands into the next. Completion is the contract date plus nine months.</p>
<h2>Scope, deliverables and completion criteria</h2>
{_detail_html()}
<h2>Execution — the phases overlap by cutover area wave</h2>
<p class="note">Windows are months after the contract date. An area returns to automatic control only when its Phase 5 programming is proved.</p>
<table><thead><tr>{"".join(f'<th class=c>{html.escape(c)}</th>' for c in WAVE_COLS)}</tr></thead>
<tbody>{_wave_html()}</tbody></table>
<h2>Quantity reconciliation — the phases cover the whole project</h2>
<table><thead><tr>{"".join(f"<th>{html.escape(c)}</th>" for c in QTY_COLS)}</tr></thead>
<tbody>{_qty_html()}</tbody></table>
<h2>Open items</h2>
<div class="grid2">{_verify_html()}</div>
<p class="foot">Generated {TODAY} · Red5-DHCP · basis: panels_schedule.json (판넬별 포인트 정리 {SRC}),
docs/reconciliation_2026-08.md, build_cutover.py, build_commissioning.py · meeting of 2026-09-03.
Print to PDF for distribution. Not legal advice — see open items.</p>
</div></body></html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


# --- Markdown --------------------------------------------------------------
def write_md(path):
    L = [f"# Red5-DHCP — continuous project delivery, by phase", "",
         SUBTITLE, "", f"_Generated {TODAY}. Basis: `panels_schedule.json` ({SRC}), the controller "
         "cutover plan and the per-panel commissioning checklist. Not legal advice._", "",
         "## One continuous delivery", "", RATIONALE, "",
         "## How the phases overlap", "", SEQUENCING, "",
         "## Stage gates", "", INDEPENDENCE, "",
         "## Phases", ""]
    for no, _c, title, nature, lic, window, objective, scope, deliv, acc, dep, cap in SEGMENTS:
        L += [f"### {no} — {title}", "",
              f"- **Nature of work:** {nature}",
              f"- **Licence question:** {lic}",
              f"- **Window:** {window}",
              f"- **Depends on:** {dep}",
              f"- **How the delivery continues:** {cap}", "",
              f"**Objective.** {objective}", "", "**Scope**", ""]
        L += [f"- {s}" for s in scope]
        L += ["", "**Deliverables**", ""] + [f"- {s}" for s in deliv]
        L += ["", "**Acceptance / completion criteria**", ""] + [f"- {s}" for s in acc] + [""]

    L += ["## Execution — interleaved by cutover area wave", "",
          "| " + " | ".join(WAVE_COLS) + " |",
          "|" + "|".join("---" for _ in WAVE_COLS) + "|"]
    for w in WAVES:
        L.append("| " + " | ".join(str(x) for x in w) + " |")
    L += [f"| **TOTAL** | | **{_WAVE_PAN}** | **{_WAVE_PTS:,}** | | | | | |", ""]

    L += ["## Quantity reconciliation", "",
          "| " + " | ".join(QTY_COLS) + " |",
          "|" + "|".join("---" for _ in QTY_COLS) + "|"]
    for row in QUANTITIES:
        L.append("| " + " | ".join(str(x) for x in row) + " |")
    L += ["", "## Open items — confirm before contracting", ""]
    for title, sev, text in VERIFY:
        L += [f"### {title} ({sev})", "", text, ""]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    stem = os.path.join(EXPORT_DIR, "red5-dhcp_phase-plan")
    write_csv(stem + ".csv")
    write_xlsx(stem + ".xlsx")
    write_html(stem + ".html")
    write_md(os.path.join(DOCS_DIR, "phase_plan.md"))

    assert len(SEGMENTS) == 5, len(SEGMENTS)
    assert _WAVE_PAN == N_PANELS, (_WAVE_PAN, N_PANELS)
    assert _WAVE_PTS == N_POINTS, (_WAVE_PTS, N_POINTS)
    assert N_ANALOG == N_AI + N_AO == 591, (N_ANALOG, N_AI, N_AO)
    assert N_BINARY + N_BTOT + N_ANALOG == N_POINTS, (N_BINARY, N_BTOT, N_ANALOG, N_POINTS)
    print(f"phase plan exported: {len(SEGMENTS)} phases over {len(WAVES)} waves, "
          f"{_WAVE_PAN} panels / {_WAVE_PTS:,} points -> {stem}.{{csv,xlsx,html}} "
          f"+ docs/phase_plan.md")
