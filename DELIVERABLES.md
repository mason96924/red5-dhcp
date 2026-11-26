# Red5-DHCP — deliverables index

One place to find every canvas, download, doc, and the script that regenerates it.
(Ask the agent "open the control-logic canvas" etc. and it will open any canvas below.)

## Canvases (interactive, open in Cursor)

Canvas files live outside the repo, in the Cursor project canvas folder:
`~/.cursor/projects/Users-jinkim-CURSOR/canvases/`

| Canvas | What it shows | File |
|--------|---------------|------|
| Panels × Controllers × I/O | Full BMS I/O pivot (16 panels, 109 controllers, 1383 pts) | `dhcp-panels-io-pivot.canvas.tsx` |
| Control logic / SOO | Per-controller Sequence of Operations | `dhcp-control-logic.canvas.tsx` |
| Controller cutover plan | BMS controller replacement, phased shoulder-season cutover | `dhcp-controller-cutover-plan.canvas.tsx` |
| Lighting I/O | Lighting-only I/O pivot | `dhcp-lighting-io-pivot.canvas.tsx` |
| Electrical I/O | Power-monitoring / electrical I/O pivot | `dhcp-electrical-io-pivot.canvas.tsx` |

To open one: click the file in Cursor, or just ask the agent to open it by name.

## Downloadable exports — `exports/` (CSV · XLSX · HTML)

| Dataset | Files (in `exports/`) |
|---------|------------------------|
| Full BMS I/O list | `red5-dhcp_full.{csv,xlsx,html}` |
| Lighting I/O | `red5-dhcp_lighting.{csv,xlsx,html}` |
| Electrical / power monitoring | `red5-dhcp_electrical.{csv,xlsx,html}` |
| Electrical switchboard / MCC schedule | `red5-dhcp_switchboard.{csv,xlsx,html}` |
| Control logic / SOO | `red5-dhcp_control-logic.{csv,xlsx,html}` |
| Per-controller commissioning checklists | `red5-dhcp_commissioning.{csv,xlsx,html}` |
| Controller cutover plan | `red5-dhcp_controller-cutover-plan.{csv,xlsx,html}` |
| Continuous delivery, by phase | `red5-dhcp_phase-plan.{csv,xlsx,html}` |
| System architecture SLD — existing vs proposed | `red5-dhcp_sld.html` · `red5-dhcp_sld-{existing,proposed}.svg` |
| Workflow plan, one project, nine months from the contract date | `red5-dhcp_workflow-plan.{csv,xlsx,html}` · `red5-dhcp_workflow-gantt.svg` |
| GCL+ control programs (Delta Controls) | `red5-dhcp_gcl-programs.{gcl,html}` |
| **Master I/O workbook** (repo root) | `../Red5-DHCP_BMS_IO_List.xlsx` |

Open the `.html` versions in any browser (search / print / copy built in); the `.xlsx`
are multi-sheet workbooks; `.csv` for import.

## Docs — `docs/`

| Doc | Contents |
|-----|----------|
| `docs/control_logic.md` | All 109 controllers' SOO in Markdown |
| `docs/gcl_programs.md` | All 109 GCL+ programs |
| `docs/R-1_control_narrative.md` | R-1 chiller control & optimisation narrative |
| `docs/phase_plan.md` | Continuous delivery in five overlapping phases |
| `docs/workflow_plan.md` | One-project workflow: workstreams, hold points, per-panel cutover, new device network |

## Regenerate anything — build scripts

Run with the repo's venv (`.venv/bin/python <script>`). Each writes to `exports/`,
`docs/`, and/or the canvas folder.

| Script | Regenerates |
|--------|-------------|
| `generate_io_list.py` | Master I/O workbook + point model (single source of truth) |
| `build_exports.py` | Full / lighting / electrical I/O exports |
| `build_switchboard.py` | Electrical switchboard / MCC schedule |
| `build_control_logic.py` | Control logic / SOO (md, csv, xlsx, html, canvas) |
| `build_commissioning.py` | Per-controller commissioning checklists |
| `build_cutover.py` | Controller cutover plan (csv, xlsx, html) |
| `build_segmentation.py` | Phase plan of the one continuous delivery (csv, xlsx, html, md) |
| `build_sld.py` | System architecture SLDs, existing vs proposed (svg, html) |
| `build_workflow.py` | One-project workflow, panel cycle, device network, hold points (csv, xlsx, html, svg, md) |
| `build_gcl.py` | GCL+ programs (md, .gcl, html) |
