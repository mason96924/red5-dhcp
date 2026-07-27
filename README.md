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
| `generate_io_list.py` | Reproducible generator for the BMS I/O list + panel / controller schedule (single source of truth for the point model) |
| `Red5-DHCP_BMS_IO_List.xlsx` | Generated deliverable — 862 points, 119 devices, 7 panels, 52 DDC controllers |
| `backend/` | FastAPI supervisory service (loads the point model, simulates live telemetry) |
| `frontend/index.html` | Read-only monitoring dashboard (systems, equipment tiles, per-device point tables) |

## Regenerate the I/O list

```bash
python3 -m venv .venv
.venv/bin/pip install openpyxl
.venv/bin/python generate_io_list.py
```

## BMS supervisory service (scaffold)

A self-contained monitor for this building. The
device / point model is imported **directly from `generate_io_list.py`** (the
import is side-effect free — the `.xlsx` is only written under its `__main__`
guard), so the dashboard and the Excel deliverable never drift apart. Until
real field I/O is wired in, `backend/sim.py` synthesizes coherent live values
from a single building driver (time-of-day load + outdoor conditions); the DHC
network is modelled as the **primary** source with the RC-1 chillers staged as
backup at high load.

```bash
.venv/bin/pip install -r requirements.txt
./run.sh                     # http://127.0.0.1:8020   (PORT=9000 ./run.sh to override)
```

Endpoints: `GET /` (dashboard), `/api/health`, `/api/snapshot` (full live
state), `/api/panels`, `/api/points` (catalog, filter by `?system=`/`?panel=`),
`/api/device/{id}`.

## Source documents (not tracked in git)

The supplied as-builts, Azbil specifications, energy workbooks and HVAC
schedules live locally as `*.zip` / `*.pdf` / `*.xlsx` and are `.gitignore`d
because of their size. Extract them into `_source/` with the helper in the
chat history, or unzip manually (inner filenames are CP932 / Shift-JIS).

Key basis documents:
- `M-01 機器表系統図(改修)` — equipment schedule / system diagram (chillers, pumps, HEX) — **the source for pump/FCU quantities**
- `共-01 工事概要及び特記仕様書` — ESCO scope (pump / OAU optimization, thermal-demand control)
- `空調機スケジュール_20251127.xlsx` — AHU/OAU operating, temperature & INV schedules
- `Azbil 納入仕様書` (144 pp, OCR'd) — **savic-netFX2 software function specification** (dated 2015/04/09), *not* an equipment list. Confirms the BMS platform and its supervisory feature set.

## Topology (OCR-verified from Azbil BMS graphics + 計装図)

- **DHC is the primary source**: chilled-water intake (冷水受入, low + high risers)
  through **HEX-1**, plus **steam intake** (蒸気受入, low @B2F / high @rooftop).
- **Local chillers RC-1 ×3 are BACKUP** with source sequence changeover (順序切替).
- **CP-8** = primary CHW pumps; **CP-7** = secondary distribution pump.
- **CT-1 / CT-2** cooling towers, two INV fans each.
- **Guest-room FCUs (4-pipe on DHC water)** are BMS-supervised as riser/orientation
  **zone-groups** — 5–20F and 20–35F, N/S/SE/SW — with batch valve-fault monitoring
  (冷水BV / 温水BV 一括故障). Individual room FCUs run on local thermostats.

## BMS platform (confirmed by OCR of the 144-page 納入仕様書)

The central station is **Azbil savic-netFX2** (S/W 機能仕様, 2015/04/09). The
delivery spec is a catalog of ~50 function-spec sheets — it defines exactly what
`BMS-CENTRAL` must provide: point management; start-stop / setpoint operation;
status, alarm & event processing; time-program + calendar + event-program
control; seasonal changeover (batch); remote-setpoint schedules; runtime /
start-count and deviation / high-low-limit monitoring; trend + periodic data
collection; daily / monthly reports; energy CSV export; numeric & logic
operations; power-failure / restoration handling; user & access management; and
maintenance / spare-parts management.

## Notes

Items still flagged **INFERRED** (hot-water pumps off the steam HEX, exact CP-7
quantity, per-group FCU counts) are **not** in the 納入仕様書 — that document is
the savic-netFX2 *software* function spec, with no equipment quantities. To
finalize them, OCR/read the **M-01 mechanical equipment schedule** in the
as-built set (`②竣工保管図書` / the 竣工図 zips).
