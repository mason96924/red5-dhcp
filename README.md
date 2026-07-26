# Red5-DHCP

BMS engineering workspace for a **District Heating & Cooling (DHC) connected**
hotel — the ANA InterContinental Tokyo (SRC, B3–37F, ~98,331 m², Azbil
savic-net BMS).

The district network supplies **steam** (low-rise main @ B2F, high-rise main @
rooftop) plus a chilled-water tie. On site, a 2015 ESCO retrofit added local
plant: water-cooled screw chillers (RC-1 ×3), primary CHW pumps (CP-8 ×3), a
plate heat exchanger (HEX-1), cooling towers and condenser pumps. Air side:
AHUs (AC-1…27), outdoor-air units (EVU-1…15), FCUs (36/37F, 4-pipe) and a large
kitchen ventilation fleet (EF/SF/RF).

## Contents

| File | Purpose |
|------|---------|
| `generate_io_list.py` | Reproducible generator for the BMS I/O list + panel / controller schedule |
| `Red5-DHCP_BMS_IO_List.xlsx` | Generated deliverable — 820 points, 115 devices, 7 panels, 48 DDC controllers |

## Regenerate the I/O list

```bash
python3 -m venv .venv
.venv/bin/pip install openpyxl
.venv/bin/python generate_io_list.py
```

## Source documents (not tracked in git)

The supplied as-builts, Azbil specifications, energy workbooks and HVAC
schedules live locally as `*.zip` / `*.pdf` / `*.xlsx` and are `.gitignore`d
because of their size. Extract them into `_source/` with the helper in the
chat history, or unzip manually (inner filenames are CP932 / Shift-JIS).

Key basis documents:
- `M-01 機器表系統図(改修)` — equipment schedule / system diagram (chillers, pumps, HEX)
- `共-01 工事概要及び特記仕様書` — ESCO scope (pump / OAU optimization, thermal-demand control)
- `空調機スケジュール_20251127.xlsx` — AHU/OAU operating, temperature & INV schedules
- `Azbil 納入仕様書` — full delivery spec / points list (scanned; needs OCR)

## Notes

Items flagged **INFERRED** in the workbook (secondary CHW distribution pumps,
hot-water pumps off the steam HEX, FCU quantities) must be confirmed against
the as-builts / Azbil 納入仕様書.
