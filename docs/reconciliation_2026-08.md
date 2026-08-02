# Red5-DHCP — document reconciliation (2026-08)

Reconciles seven newly-supplied Azbil drawing/graphic PDFs against the model
identified so far (`generate_io_list.py`, `panels_schedule.json`, `README.md`).
Read by direct image analysis of rasterized pages, not OCR.

## 1. Source inventory

| # | File | Pages | What it actually is | Status |
|---|------|:----:|---------------------|--------|
| 1 | `Azbil 完成図.pdf` | 16 | savic-net FX summary graphics (heat source 全体/低層/高層/36,37F/冷却塔/ホットウェル/DHC受入) | already the primary source |
| 2 | `Azbil サマリーグラフ空調関連.pdf` | 20 | air-side (AHU/OAU) summary graphs | already used |
| 3 | `アズビル サマリーグラフ客室等.pdf` | 28 | guest-room / floor summary graphs | already used |
| 4 | `アズビル BMS サマリーグラフ画面.pdf` | 18 | **NEW** — live **savic-net FX operator summary screens** (graph IDs 3001…5000+) | **new subsystems surfaced** |
| 5 | `Central monitoring system (hardware).pdf` | 34 | **NEW** — **Azbil savic-netFX2 ESCO delivery spec** (工番 1-LHP1-11, 2015/04/09): central-station hardware + fieldbus architecture | **central/comms architecture** |
| 6 | `Communication System Diagram.pdf` | 1 | **NEW** — **伝送幹線系統図** (BEMS transmission trunk, dwg A-20, 2002): every panel by floor + UIC transmission lines | **panel↔bus topology** |
| 7 | `Instrumentation diagram.pdf` | 14 | **NEW** — ESCO **自動制御 詳細図** (A-1…A-14, 2002): per-AHU UC-controller I/O + heat-source P&ID | validates air-side + DHC model |

## 2. Central monitoring architecture — *newly precise* (was generic "BMS-CENTRAL")

From the savic-netFX2 delivery spec (#5, drawings LHP1-11-200-01/02, -100-B0xx, -202-xx):

- **Platform:** Azbil **savic-netFX2** — confirms the platform previously inferred
  from the 144-page 納入仕様書.
- **Servers (on the Ethernet backbone):**
  - **BMS** building-management server — NEC **FC-E21A** (`ビルマネジメントサーバ`).
  - **SMS** system-management server + **DSS** data-storage server — Azbil SI-net
    (`BCY45300W0020` / `BCY46300W0020`).
- **Operator consoles:**
  - **監視用PC1** (Fujitsu ESPRIMO D551/G) — **B2F 防災室**, panel `LHP1-11-101`.
  - **監視用PC2** (Fujitsu ESPRIMO D551/G) — **2F 防災センター**, panel `LHP1-11-103`.
  - EIZO 22″ LCDs (`EV2216W`, 1680×1050); **CLP** = Brother `HL-4570CDW` colour laser.
- **Network:** IPv4/IPv6 Ethernet, 100BASE-TX with fibre risers between floors.
  Switches: **ESW1** (Hitachi APLGB108SS, 8-port) in 101, **ESW3** (8-port) in 103,
  **ESW2** (Allied Telesis FS816S, **16-port**) in the system-control panel 102.
  IP plan `192.168.30.x` / `192.168.31.x` (address table on -200-02).

### Fieldbus hierarchy (this replaces the flat "12 panels / 84 DDC" abstraction)

- **6 × SCS — システム・コア・サーバ (System Core Server)** `BCY44200W0000`, mounted in
  system-control panel 102, all on **ESW2**.
- **Each SCS heads up to 4 NC-bus lines** (`NC-bus 1〜4ライン`). → up to **24 NC-bus
  segments** total.
- **Each NC-bus line is a daisy-chain of RS (Remote Stations) + DDC (digital
  controllers)** over transmission trunk **IPEV-S 0.9 mm²** (TX-IN → TX-OUT).
- **IFGD1** — Inf-GD base module with **DI 16 / DO 8** for fire-alarm & external
  signals (`火災入力・外部信号等用`).

> **The RS remote stations are the 67 physical panels** in `panels_schedule.json`
> (`RS-*`, `RCP-*`, `CP-*`). So the physical reality is
> **6 SCS → ≤24 NC-bus lines → 67 RS/DDC**. The functional model (now 16 logical
> panels / 109 DDC after this reconciliation) is a *role-based abstraction* — one
> logical controller per equipment group; keep it for the SOO/GCL+, but the network
> drawings show the true segmentation. Documented in the workbook's `Comms-Network` sheet.

## 3. Transmission trunk topology (#6, 伝送幹線系統図, 2002)

Floor-segmented trunk. Named **LINE** segments (`UIC1-1/1-2`, `UIC2-1…2-4`,
`UIC3-1/3-2` = high-rise risers to 10F/21F/31F, `UIC4-1…4-3` + `UIC4-C` = basements)
each daisy-chain that zone's `RS/RCP/CP` panels. Panel names and their attached
equipment **match the 26.07.30 physical schedule** — e.g. PH1F shows
`AC-24 · EVU-11 · EVU-13 → RCP-PH1-2`, matching panel #6. This is the **2002
base-building trunk that the 2015 SCS/NC-bus retrofit rides on** (UIC lines ≈ the
earlier equivalent of the NC-bus lines).

## 4. Instrumentation / air-side (#7, 自動制御 詳細図, 2002)

- Per-AHU **改修前 → 現状** control sheets for **AC-1…AC-27**, each showing the
  **UC (unit controller)** with its `DO/DI/AO/AI` module counts, **MTV** modulating
  valves, **INV/VFD** fan drives, and the **動力盤 (`RCP-*`)** it lands on.
- **CO₂ demand-controlled ventilation** on banquet AHUs **AC-11 / AC-12 / AC-13**
  (`CO2制御 AO-11〜13`), 3 sets — a point set worth adding explicitly.
- Heat-source P&ID (sheet A-1): DHC **CSH/CRH** headers, **EX** heat exchangers,
  seasonal **冷水/温水 changeover per floor-group** (5–9F/10F/11–20F/21–30F/31–37F),
  R-1 side — **confirms the DHC-primary + local-backup topology** in the README.

## 5. Supervised subsystems surfaced by the live BMS screens (#4)

These appear in the operator summary screens (and are already counted in the
4,467-point physical schedule) but are **not named as devices** in the current
190-device functional model:

| Graph ID | Screen | Tags / scope |
|---|---|---|
| 4100 | **給湯 (DHW)** 系統図 | steam-heated storage `ST-1-1…4 / ST-2-1/2 / ST-3-1/2 / ST-4-1/2`; DHW **zone pumps `HP-1` (B3F–5F), `HP-2` (5F–15F), `HP-3` (16F–25F), `HP-4` (26F–37F)**; storage steam-flow metering |
| 4200 | **衛生 上水・中水** 系統図 | potable (上水) + reclaimed (中水): booster sets `MP-1…4`, `P-1…6`, tanks `WT-*`/`T-1…6`, 受水槽/高置水槽/消火水槽/中水受水槽, pressure tanks |
| 4300 | **排水 (drainage)** 系統図 | sump/sewage pumps `DP-1…14` (湧水/雑排水/汚水/トレンチ), aeration blowers `BL-1-1/2, BL-2-1/2, BL-F-1/2` for 厨房排水処理槽 + 雨水槽 |
| 4400 | **ろ過装置 (filtration)** | 浴室(男/女) 5F, サウナ+水風呂 4F, プール 3F, 大滝/雲海庭園の滝, ロータリー噴水 B2F, 雨水 B3F — filtration + circulation |
| 5000 | **排煙 (smoke exhaust)** 系統図 | smoke-exhaust fans `SMF-1…22`, 火災一括, per floor B3F…PH2F |
| 3001+ | **照明 (lighting)** 一覧 | stairwell `A〜K階段` + `消防用階段` by floor band; `外灯 1…11` + `1L-11/1L-12` (ELR) |

## 6. Reconciliation summary

**Confirmed** (no change): savic-netFX2 platform; DHC-primary + `R-1` Ebara screw
backup + condenser-water/cooling-tower topology; AHU `AC-1…27`; guest-room FCU
orientation groups; the 67-panel physical schedule (names match the trunk drawing).

**Refined:**
- Central + comms architecture is now concrete (servers, 2 consoles + locations,
  switches, IP plan) — see §2. README updated.
- **`HP-1…4` are DHW zone supply pumps** on steam-heated storage, grouped by
  vertical zone — not generic "hot-water heating pumps ×3".
- Controller hierarchy is **6 SCS → ≤24 NC-bus lines → RS/DDC (67 panels)**.

**Gaps in the *functional* device model — now CLOSED (2026-08-03).**
`generate_io_list.py` was extended with the five device groups below and a
`Comms-Network` sheet; all downstream deliverables were regenerated. The
functional model grew **1,160 → 1,383 points · 190 → 259 devices · 12 → 16 panels
· 84 → 109 DDC controllers**:

1. **DHW** (`LCP-DHW`, System *Domestic hot water*) — `DHW-1…4` steam-heated storage
   + zone supply/recirc pumps by vertical zone (drawing tags `ST-*`/`HP-1…4` cited in
   notes to avoid the OA-station / heat-source-pump tag collision). *28 pts.*
2. **Sanitary/plumbing** (`LCP-SAN`) — potable/reclaimed booster `MP-1…4`/`P-1…6`,
   receiving/elevated/fire tanks, drainage sumps `DP-1…14`, aeration blowers `BL-*`. *101 pts.*
3. **Filtration** (`LCP-FILT`) — bath/sauna/waterfall/fountain/rainwater `ろ過装置`
   groups (pool remains `POOL-FP`). *24 pts.*
4. **Smoke exhaust** (`LCP-SMK`) — `SMF-1…22` + fire batch `SMK-FIRE` (life-safety
   start hard-wired; BMS monitors + smoke-mode start). *67 pts.*
5. **CO₂ DCV** — `AC-11/12/13.CO2` + DCV note on the OA damper. *3 pts.*

Each new group has a Sequence-of-Operations class in `build_control_logic.py` and a
GCL+ program. Central + fieldbus architecture (§2) is captured in the workbook's
`Comms-Network` sheet.
