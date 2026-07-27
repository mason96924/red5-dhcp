# Red5-DHCP

BMS engineering workspace for a **District Heating & Cooling (DHC) connected**
hotel — the ANA InterContinental Tokyo (SRC, B3–37F, ~98,331 m², Azbil
**savic-net FX / FX2** BMS).

The device/point model was **rebuilt from a direct reading of the Azbil 完成図
savic-net graphics** (熱源設備 全体/低層/高層/36,37F/冷却塔/ホットウェル/DHC受入,
graph IDs 1000–1100), the air-side summary graphs (空調関連 / 客室等) and the
`M-*` CAD equipment schedules.

The district network is the **primary heat source**: DHC **chilled water**
(冷水受入, CS/CR headers, GJ-metered) and DHC **steam** (蒸気受入, 0.8 → 0.2 MPa,
condensate returned to a hot well). Local plant is **backup/peaking**:
- **Low-rise (低層)** — `CP-1 ×3` primary CHW + `HP-1 ×3` hot-water pumps, `EX-2`
  laundry HX, `CP-4/CP-5` kitchen pumps, `EXT-1`, `ST-1` OA station.
- **High-rise (高層)** — `CP-2 ×3` primary CHW + `HP-2 ×3` hot-water pumps,
  `CP-3` (INV) / `CP-6`, `EX-3` HX, `EXT-2`, `ST-2` OA station.
- **36/37F (熱源設備 36,37F系統)** — `R-1`, a **single water-cooled screw chiller**
  (Ebara **RHS DW202M2**, エバラスクリュー冷凍機: 370 kW cooling / 82.2 kW input →
  **COP 4.5**, twin 45 kW screw compressors, dual R-407C circuits, 2014-12) run in
  **changeover with DHC** via `HEX-1` + `CP-8`; `CDP-3` + `CT-3` condenser, `CP-7`
  CHW pumps, `HP-4` + `EX4` + `EXT-3` secondary, and two DHC↔R-1 changeover valves.
- **Condenser water (冷却塔)** — `CT-1` (2 INV cells) + `CT-2` (2 cells +
  filtration) with `CDP-1 ×3` / `CDP-2 ×2` pumps rejecting heat from **packaged
  units** (PCU/PAC/PMAC) and **kitchen refrigeration**; `EX-1` winter free-cooling
  HX; two emergency cooling HX tied back to the DHC chilled headers.

Air side: AHUs (`AC-1…27`), outdoor-air units (`EVU-1…15`), guest-room FCU
zone-groups (5–20F & 21–35F × **N/NE/SE/S/SW**, 4-pipe) + 36/37F FCU, and a large
kitchen ventilation fleet (`EF/SF/RF`). Also on the savic-net: packaged units,
kitchen-refrigeration alarms and common-area/façade lighting (照明一覧).

## Contents

| File | Purpose |
|------|---------|
| `generate_io_list.py` | Reproducible generator for the BMS I/O list + panel / controller schedule (single source of truth for the point model) |
| `Red5-DHCP_BMS_IO_List.xlsx` | Generated deliverable — 1,160 points, 190 devices, 12 panels, 84 DDC controllers |
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
network is modelled as the **primary** source with the local `R-1` chiller
staged as backup at high load and its DHC↔R-1 changeover valves following suit.

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
- `Azbil 完成図.pdf` — **savic-net FX BMS summary graphics** (graphs 1000–1100:
  熱源設備 全体/低層/高層/36,37F/冷却塔/ホットウェル/DHC受入; PMAC/PAC一覧; 照明一覧).
  **This is the primary source for the heat-source topology, tags and points.**
- `Azbil サマリーグラフ空調関連.pdf` / `アズビル サマリーグラフ客室等.pdf` — per-unit
  AHU/OAU graphics + guest-floor plans (air-side inventory & point set).
- `M-01 機器表系統図(改修)` / `M-02` — retrofit equipment schedule / system diagram
  (`R-1` replacing the demolished chiller; pump/FCU quantities).
- `共-01 工事概要及び特記仕様書` — ESCO scope (pump / OAU optimization, thermal-demand control).
- `空調機スケジュール_20251127.xlsx` — AHU/OAU operating, temperature & INV schedules.
- `Azbil 納入仕様書` (144 pp, OCR'd) — **savic-net FX2 software function specification**
  (dated 2015/04/09), *not* an equipment list. Confirms the BMS platform + feature set.

## Topology (read directly from the Azbil savic-net graphics)

- **DHC is the primary source** — DHC chilled water (冷水受入 `CS`/`CR`, GJ/h + m³/h +
  P/T metering) and DHC steam (蒸気受入 `SS` 0.8 MPa → PRV 8k→2k → 0.2 MPa; condensate
  `HR` metered back to the **hot well `HWT-1`**, returned via `HP-5`; `HP-3` feeds the
  B1F kitchen AHUs `AC-5/6/7`).
- **`R-1` is a single 36/37F backup screw chiller** — Ebara **RHS DW202M2**
  (nameplate-confirmed: 370 kW / COP 4.5, twin screw, R-407C) — *not* the fabricated
  "RC-1 ×3" plant. It runs in **changeover with DHC** (`HEX-1` + `CP-8`)
  via two valves (`CHGV-1` R-1 branch / `CHGV-2` DHC bypass); `CDP-3`+`CT-3` condenser,
  `CP-7` CHW, `HP-4`+`EX4`+`EXT-3` secondary distribution to the 36/37F loads.
- **Condenser water rejects packaged-unit + refrigeration heat** (not main chillers):
  `CT-1`/`CT-2` (INV cells, filtration, `E/H` basin heaters, 薬注 dosing, 渇水 alarms)
  with `CDP-1 ×3` / `CDP-2 ×2`; `EX-1` winter free-cooling; 2 emergency cooling HX to DHC.
- **Distribution pumps are sequenced groups** (順序 / 群起動): `CP-1 ×3` & `CP-2 ×3`
  primary CHW, `HP-1 ×3` & `HP-2 ×3` hot-water, plus `CP-3`(INV)/`CP-6`, `CP-4`/`CP-5`.
- **Guest-room FCUs (4-pipe)** are BMS-supervised as **orientation zone-groups** —
  5–20F and 21–35F, each **N/NE/SE/S/SW** — with batch valve-fault monitoring
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

Device tags, counts and point sets were read directly from the savic-net
graphics, so the heat-source model no longer carries the earlier fabricated
"RC-1 ×3" plant. Two areas are modelled as **representative supervised groups**
rather than one row per physical unit:
- **Packaged units** (`PCU`/`PAC`/`PMAC`) — the tagged units from the PMAC/PAC一覧
  are included with status/alarm/start-stop; the full room-by-room fleet can be
  expanded from that sheet.
- **Common-area / façade lighting** — `LTG-*` groups summarise the 照明一覧 1/2
  schedules (per-floor 間接/ブラケット照明, corridors, lobbies, soffits, balcony,
  neon, aviation light); expand per floor for a full point count.
