"""build_commissioning.py -- per-controller point-to-point commissioning sheets.

For every DDC controller in the model, emit a field checklist of its points with
tick-box columns (wired / terminated / P2P verified / functional test) plus
observed-value and notes fields, in three portable forms under exports/:

  red5-dhcp_commissioning.xlsx   Index + one worksheet per controller
  red5-dhcp_commissioning.html   interactive: clickable checkboxes, search,
                                 one print page per controller (print-to-PDF)
  red5-dhcp_commissioning.csv    combined flat sheet (Panel/Controller columns)

Carried by the field crew during each controller swap (see the cutover plan).
"""
from __future__ import annotations

import csv
import datetime
import html
import os

import generate_io_list as g

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(HERE, "exports")
TODAY = datetime.date.today().isoformat()

CHECK_COLS = ["Wired", "Terminated", "P2P verified", "Func. test"]
BASE_COLS = ["#", "Point Tag", "Device", "Description", "I/O", "Signal / Range", "Units"]
TAIL_COLS = ["Observed value / state", "Notes"]
BOX = "\u2610"  # ballot box

PANEL_META = {p[0]: (p[1], p[2]) for p in g.PANELS}  # id -> (desc, location)


def controllers_in_order():
    """(cid, panel, devices, points[]) grouped, in panel/controller order."""
    ctrl_pts = {}
    for r in g.rows:
        ctrl_pts.setdefault(r["Controller"], []).append(r)
    panel_order = [p[0] for p in g.PANELS]
    ordered = sorted(
        g.controllers,
        key=lambda c: (panel_order.index(c[1]) if c[1] in panel_order else 99, c[0]),
    )
    out = []
    for cid, panel, devices in ordered:
        pts = ctrl_pts.get(cid, [])
        if pts:
            out.append((cid, panel, devices, pts))
    return out


# ---------------------------------------------------------------------------
# CSV (combined)
# ---------------------------------------------------------------------------
def write_csv(path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Panel", "Controller", "Devices served"] + BASE_COLS[1:] + CHECK_COLS + TAIL_COLS)
        for cid, panel, devices, pts in controllers_in_order():
            for i, r in enumerate(pts, 1):
                w.writerow([panel, cid, devices, r["Point Tag"], r["Device ID"],
                            r["Point Description"], r["I/O Type"], r["Signal / Range"],
                            r["Units"], BOX, BOX, BOX, BOX, "", ""])


# ---------------------------------------------------------------------------
# XLSX (index + sheet per controller)
# ---------------------------------------------------------------------------
def write_xlsx(path):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    HDR = PatternFill("solid", fgColor="1F3864")
    HF = Font(bold=True, color="FFFFFF", size=10)
    CHK = PatternFill("solid", fgColor="FFF6D9")
    thin = Side(style="thin", color="D9D9D9")
    B = Border(left=thin, right=thin, top=thin, bottom=thin)
    ctr = Alignment(horizontal="center", vertical="center")
    top = Alignment(wrap_text=True, vertical="top")

    ctrls = controllers_in_order()
    cols = BASE_COLS + CHECK_COLS + TAIL_COLS
    widths = [4, 16, 12, 34, 6, 16, 8] + [11, 11, 12, 10] + [22, 24]

    wb = Workbook()
    idx = wb.active
    idx.title = "Index"
    idx.append(["Red5-DHCP — per-controller commissioning checklists"])
    idx.cell(row=1, column=1).font = Font(bold=True, size=14, color="1F3864")
    idx.append([f"Generated {TODAY}  ·  {len(ctrls)} controllers  ·  {len(g.rows)} points"])
    idx.cell(row=2, column=1).font = Font(italic=True, size=10, color="555555")
    idx.append([])
    idx.append(["Panel", "Controller", "Devices served", "Points", "Sheet"])
    hrow = idx.max_row
    for c in range(1, 6):
        idx.cell(row=hrow, column=c).fill = HDR
        idx.cell(row=hrow, column=c).font = HF

    for cid, panel, devices, pts in ctrls:
        sheet = cid[:31]
        rr = idx.max_row + 1
        idx.append([panel, cid, devices, len(pts), sheet])
        link = idx.cell(row=rr, column=5)
        link.hyperlink = f"#'{sheet}'!A1"
        link.font = Font(color="1F5FBF", underline="single")
    for i, wdt in enumerate([14, 14, 60, 8, 14], 1):
        idx.column_dimensions[get_column_letter(i)].width = wdt
    for rr in range(hrow, idx.max_row + 1):
        for c in range(1, 6):
            idx.cell(row=rr, column=c).border = B
            idx.cell(row=rr, column=c).alignment = top
    idx.freeze_panes = "A5"

    for cid, panel, devices, pts in ctrls:
        ws = wb.create_sheet(cid[:31])
        desc, loc = PANEL_META.get(panel, ("", ""))
        ws.append([f"Commissioning checklist — {cid}"])
        ws.cell(row=1, column=1).font = Font(bold=True, size=13, color="1F3864")
        ws.append([f"Panel {panel} ({desc})", "", f"Location: {loc}"])
        ws.append([f"Devices served: {devices}"])
        ws.append(["Technician: ______________________", "", "Date: __________",
                   "", "Signature: ______________________"])
        ws.append([])
        hr = ws.max_row + 1
        ws.append(cols)
        for c in range(1, len(cols) + 1):
            ws.cell(row=hr, column=c).fill = HDR
            ws.cell(row=hr, column=c).font = HF
            ws.cell(row=hr, column=c).alignment = ctr
        chk_start = len(BASE_COLS) + 1
        chk_end = len(BASE_COLS) + len(CHECK_COLS)
        for i, r in enumerate(pts, 1):
            ws.append([i, r["Point Tag"], r["Device ID"], r["Point Description"],
                       r["I/O Type"], r["Signal / Range"], r["Units"],
                       BOX, BOX, BOX, BOX, "", ""])
            rr = ws.max_row
            for c in range(chk_start, chk_end + 1):
                cell = ws.cell(row=rr, column=c)
                cell.fill = CHK
                cell.alignment = ctr
                cell.font = Font(size=12)
        for i, wdt in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = wdt
        for rr in range(hr, ws.max_row + 1):
            for c in range(1, len(cols) + 1):
                ws.cell(row=rr, column=c).border = B
                if not (chk_start <= c <= chk_end):
                    ws.cell(row=rr, column=c).alignment = top
        ws.freeze_panes = f"A{hr + 1}"

    wb.save(path)


# ---------------------------------------------------------------------------
# HTML (interactive; one print page per controller)
# ---------------------------------------------------------------------------
def write_html(path):
    ctrls = controllers_in_order()

    def esc(s):
        return html.escape(str(s if s is not None else ""))

    blocks = []
    for cid, panel, devices, pts in ctrls:
        desc, loc = PANEL_META.get(panel, ("", ""))
        search_blob = esc((cid + " " + panel + " " + devices).lower())
        rows = []
        for i, r in enumerate(pts, 1):
            rows.append(
                "<tr><td class=c>{i}</td><td>{tag}</td><td>{dev}</td><td>{d}</td>"
                "<td class=c>{io}</td><td>{sig}</td><td>{u}</td>"
                "<td class=c><input type=checkbox></td><td class=c><input type=checkbox></td>"
                "<td class=c><input type=checkbox></td><td class=c><input type=checkbox></td>"
                "<td><input class=t type=text></td><td><input class=t type=text></td></tr>".format(
                    i=i, tag=esc(r["Point Tag"]), dev=esc(r["Device ID"]),
                    d=esc(r["Point Description"]), io=esc(r["I/O Type"]),
                    sig=esc(r["Signal / Range"]), u=esc(r["Units"])))
        blocks.append(
            f'<details class="ctrl" data-s="{search_blob}"><summary>{esc(cid)}'
            f'<span class="r">{esc(panel)} · {len(pts)} points</span></summary>'
            f'<div class="hd"><div>{esc(panel)} — {esc(desc)} · <em>{esc(loc)}</em></div>'
            f'<div>Serves: {esc(devices)}</div>'
            f'<div class="sign">Technician <input class=t type=text> &nbsp; Date <input class=t type=text>'
            f' &nbsp; Signature <input class=t type=text></div></div>'
            '<table><thead><tr><th class=c>#</th><th>Point Tag</th><th>Device</th><th>Description</th>'
            '<th class=c>I/O</th><th>Signal / Range</th><th>Units</th>'
            '<th class=c>Wired</th><th class=c>Term.</th><th class=c>P2P</th><th class=c>Func.</th>'
            '<th>Observed</th><th>Notes</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></details>')

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Red5-DHCP — commissioning checklists</title>
<style>
  :root {{ --ink:#1b2430; --dim:#5b6675; --line:#d5dbe4; --band:#1F3864; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:13px/1.45 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
          color:var(--ink); background:#f4f6f9; padding:24px; }}
  .wrap {{ max-width:1200px; margin:0 auto; }}
  h1 {{ font-size:21px; margin:0 0 2px; }} .sub {{ color:var(--dim); margin:0 0 14px; }}
  .bar {{ position:sticky; top:0; background:#f4f6f9; padding:8px 0 12px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; z-index:5; }}
  input[type=search] {{ border:1px solid var(--line); border-radius:7px; padding:7px 10px; min-width:280px; font-size:13px; }}
  button {{ border:1px solid var(--line); background:#fff; border-radius:7px; padding:6px 11px; cursor:pointer; font-size:12px; }}
  details.ctrl {{ background:#fff; border:1px solid var(--line); border-radius:9px; margin:0 0 10px; }}
  summary {{ padding:11px 14px; font-weight:600; cursor:pointer; list-style:none; }}
  summary::-webkit-details-marker {{ display:none; }}
  summary .r {{ float:right; color:var(--dim); font-weight:400; font-size:12px; }}
  .hd {{ color:var(--dim); font-size:12px; padding:0 14px 8px; }}
  .hd .sign {{ margin-top:6px; color:var(--ink); }}
  table {{ border-collapse:collapse; width:100%; font-size:12px; }}
  th, td {{ border:1px solid var(--line); padding:5px 7px; text-align:left; vertical-align:top; }}
  thead th {{ background:var(--band); color:#fff; position:sticky; top:52px; }}
  td.c, th.c {{ text-align:center; white-space:nowrap; }}
  input.t {{ width:100%; border:0; border-bottom:1px solid var(--line); font-size:12px; padding:2px 0; }}
  input[type=checkbox] {{ width:16px; height:16px; }}
  .hidden {{ display:none !important; }}
  .foot {{ color:var(--dim); font-size:12px; margin-top:18px; }}
  @media print {{
    body {{ background:#fff; padding:0; }} .bar {{ display:none; }}
    details.ctrl {{ break-inside:avoid; page-break-after:always; border:0; }}
    details.ctrl[open] summary .r {{ color:#000; }}
    details:not([open]) {{ display:none; }}
    thead th {{ position:static; }}
  }}
</style></head>
<body><div class="wrap">
<h1>Red5-DHCP — per-controller commissioning checklists</h1>
<p class="sub">{len(ctrls)} DDC controllers · {len(g.rows)} points. Point-to-point verify each I/O, then trend 24–48 h before returning to auto. Fill on a tablet or print to PDF (one page per controller).</p>
<div class="bar">
  <input type="search" id="q" placeholder="find controller / panel / device\u2026">
  <button id="expand">Expand all</button>
  <button id="collapse">Collapse all</button>
  <button onclick="window.print()">Print / Save PDF</button>
  <span class="sub" id="count"></span>
</div>
{"".join(blocks)}
<p class="foot">Generated {TODAY} · source: generate_io_list.py · Red5-DHCP savic-net FX2 → new DDC migration.</p>
</div>
<script>
const items=[...document.querySelectorAll('details.ctrl')];
document.getElementById('count').textContent=items.length+' controllers';
document.getElementById('q').addEventListener('input',e=>{{
  const s=e.target.value.trim().toLowerCase();
  let n=0;
  for(const d of items){{const hit=!s||d.dataset.s.includes(s);d.classList.toggle('hidden',!hit);if(hit)n++;d.open=!!s&&hit;}}
  document.getElementById('count').textContent=n+' / '+items.length+' controllers';
}});
document.getElementById('expand').onclick=()=>items.forEach(d=>d.open=true);
document.getElementById('collapse').onclick=()=>items.forEach(d=>d.open=false);
</script>
</body></html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


if __name__ == "__main__":
    os.makedirs(EXPORT_DIR, exist_ok=True)
    stem = os.path.join(EXPORT_DIR, "red5-dhcp_commissioning")
    write_csv(stem + ".csv")
    write_xlsx(stem + ".xlsx")
    write_html(stem + ".html")
    n = len(controllers_in_order())
    print(f"commissioning sheets: {n} controllers, {len(g.rows)} points -> {stem}.{{csv,xlsx,html}}")
