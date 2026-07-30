# Red5-DHCP — downloadable pivots

Shippable, offline copies of the BMS I/O model and the ESCO electrical schedule.
Each dataset comes in three forms:

| Form | Open with | Notes |
|------|-----------|-------|
| `.csv`  | Excel / Sheets / any text editor | flat point list, UTF-8-BOM |
| `.xlsx` | Excel | `Summary` + collapsible `Pivot` (Panel▸Controller▸Point outline) + `Flat` with auto-filter |
| `.html` | any web browser | self-contained interactive pivot (search + expand/collapse); no server needed |

## Datasets

| File stem | Scope | Panels / Ctrls / Points |
|-----------|-------|--------------------------|
| `red5-dhcp_full`        | Every DDC panel → controller → point in the savic-net FX2 model | 11 · 84 · 1160 |
| `red5-dhcp_lighting`    | Common-area & facade lighting (照明一覧, `LCP-LTG`) | 1 · 3 · 16 |
| `red5-dhcp_electrical`  | Electrical cross-cut: energy meters, per-device kW, electrical-protection points | 7 · 26 · 62 |
| `red5-dhcp_switchboard` | ESCO retrofit power-panel / MCC schedule (RC-1 chiller + CP-8 pump feeders) | 3 panels · 7 circuits · 90.7 kW |
| `red5-dhcp_controller-cutover-plan` | savic-net FX2 → new DDC replacement plan (Apr–May shoulder-season phasing), re-based on the 26.07.30 physical schedule, phases grouped by each panel's own floor | 67 panels · 4467 points · 4 phases (per-phase panel/point counts sum to full I/O); HTML is print-to-PDF |
| `red5-dhcp_commissioning` | Per-**panel** point-to-point checklists (tick-box: wired/terminated/P2P/func), driven by the 26.07.30 physical schedule; sheets carry floor + equipment served | 64 panels · 4467 points; XLSX = index + sheet/panel, HTML = clickable + 1 print page/panel; positional tags (panel+type+index) |
| `red5-dhcp_control-logic` | Per-controller Sequence of Operations (equipment-class SOO referencing actual tags) | 84 controllers; also `docs/control_logic.md`; XLSX = index + SOO+points per controller |
| `Red5-DHCP-Panels-IO` | Physical panel schedule (Delta controllers & modules) from the 26.07.30 Excel — with each panel's **floor** and **equipment served** (AC/EVU/SF/EF/PCU) — reconciled against the functional point list | 67 panels · 904 controllers+modules · 4467 used / 5240 cap; overlap 1160 / new-TBD 3307; 26 panels name served equipment; XLSX = `Panel schedule` + `Summary` |

The first three are generated from the device/point model in
[`../generate_io_list.py`](../generate_io_list.py); the switchboard schedule is
transcribed from the as-built electrical drawings. `Red5-DHCP-Panels-IO`,
`red5-dhcp_commissioning` and `red5-dhcp_controller-cutover-plan` are all driven by
`../panels_schedule.json`, transcribed from
`판넬별 포인트 정리(델타 컨트롤러 및 모듈 포함)_26.07.30.xlsx` (the authoritative physical
panel/module schedule). The 26.07.30 revision adds each panel's **floor** and the
**equipment it serves** (AC-* AHUs, EVU-* OAUs, SF/EF vent fans, PCU packaged units),
which ties the RCP/CP panels directly to the functional model. It still carries
per-panel type counts (DO/DI/BTOT/AI/AO), not individual point tags, so exact
point-by-point mapping to the functional list can't be resolved from this file alone.

## Regenerate

```bash
cd red5-dhcp
.venv/bin/python build_exports.py       # full / lighting / electrical
.venv/bin/python build_switchboard.py   # switchboard schedule
.venv/bin/python build_cutover.py       # controller-replacement cutover plan
.venv/bin/python build_commissioning.py # per-panel point-to-point checklists (from panels_schedule.json)
.venv/bin/python build_control_logic.py # per-controller Sequence of Operations (+ docs/control_logic.md)
.venv/bin/python build_panels_io.py     # physical panel schedule (Red5-DHCP-Panels-IO, from panels_schedule.json)
```

## Sources

- BMS model: Azbil savic-net FX2 完成図 graphics + M-01/M-02 equipment schedules.
- Switchboard: `E-01 動力制御盤改修図`, `E-02 幹線動力設備平面図`,
  `13-4 動力盤改造図` (2015-04-30, (株)ヤマグチ). Scope is limited to the circuits the
  energy-saving retrofit touched (PH1F machine-room panels feeding the RC-1 chiller
  and the new CP-8 pump); the whole-building substation and per-floor panelboards
  are not part of that drawing set.

> An in-IDE interactive version of each pivot also exists as a Cursor Canvas
> (`dhcp-panels-io-pivot`, `dhcp-lighting-io-pivot`, `dhcp-electrical-io-pivot`).
> Canvases render only inside Cursor; use the `.html` files for a portable copy.
