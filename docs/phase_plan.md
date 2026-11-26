# Red5-DHCP — continuous project delivery, by phase

One contract for the 67-panel / 4,467-point savic-netFX2 → Delta retrofit. Five phases overlap across nine months. The completion date is the contract date plus nine months. DEJ holds the contract. TYBMS is subcontracted to DEJ.

_Generated 2026-11-26. Basis: `panels_schedule.json` (26.07.30), the controller cutover plan and the per-panel commissioning checklist. Not legal advice._

## One continuous delivery

This is one continuous delivery. Fabrication, the new device network, installation, instruments and programming overlap inside the same nine months, under the one contract. The phases name the kind of work.

## How the phases overlap

Phase 5 authoring starts in month C+1 so the factory can bench-load. Phase 2 proves each new network run before that wave's first panel. On site, installation, instruments and programming happen inside the same area wave, the same night. An area returns to automatic control only when its program is proved. The playbook covers one panel at a time.

## Stage gates

The commissioning checklist still records progress: factory acceptance, Wired and Terminated, P2P verified, and Func. test. Those columns are stage gates of the one delivery. They are not separate completion contracts.

## Phases

### Phase 1 — Panel fabrication, supply & factory acceptance

- **Nature of work:** Off-site manufacture / supply
- **Licence question:** Likely NOT 建設業 (goods manufacture + supply) — confirm
- **Window:** C+0 to C+6 mo
- **Depends on:** —
- **How the delivery continues:** Hands panels to Phase 3 in wave order. Bench-load needs the programs from Phase 5, which starts in month C+1.

**Objective.** Deliver every DDC panel to site already built, loaded and factory-tested, so that on-site time is reduced to swapping an enclosure and landing wires.

**Scope**

- Procure 904 Delta controllers and I/O modules against the panel schedule
- Build and wire 67 enclosures to 5,240-point capacity (4,467 used, 773 spare)
- Head-end hardware: replacement of the BMS / SMS / DSS server role and the two operator consoles
- Bench-load the GCL+ programs and simulate I/O at the factory
- Panel general-arrangement and termination drawings, spares schedule

**Deliverables**

- 67 panels delivered to site, labelled per the panel schedule
- FAT certificate per panel (module count, addressing, power-up, simulated I/O)
- As-built panel drawings + terminal schedules
- Head-end hardware delivered and staged
- Spare-parts list and recommended holding

**Acceptance / completion criteria**

- Module count reconciles to 904 against panels_schedule.json
- FAT witnessed and signed per panel; no panel ships on a failed FAT
- Delivery note signed at site — this is the transfer of title, no site work involved

### Phase 2 — Device-network cabling

- **Nature of work:** New field network, inside the same contract
- **Licence question:** Same licence question as the site electrical work — confirm
- **Window:** C+0 survey · C+2 to C+6 install · proved before each wave
- **Depends on:** Starts with Phase 1, in the contract month
- **How the delivery continues:** Each cutover wave lands on a run this phase has already proved.

**Objective.** Identify the installed Azbil cable and, where it is IEIEJ p-A or otherwise unsuitable, install a new device network before cutover. This phase does not add a month.

**Scope**

- Survey panels and risers. The 2002 drawing names IPEV-S 0.9 mm². The installed cable may be IEIEJ p-A.
- Reuse a run only when a test shows it meets the new network specification. IEIEJ p-A is not assumed reusable.
- Design and pull the new risers and floor cabling while the old network is still in service
- Prove continuity, insulation and communications on each run before that wave starts
- Record abandoned cable so a later crew does not land a new panel on it

**Deliverables**

- Cable identification record
- Reuse or replace decision per riser
- Network drawings and cable schedule
- Segment test certificate before each wave
- As-built network drawings

**Acceptance / completion criteria**

- Cable type recorded before the network design is approved
- Each wave's new run tested before that wave's first panel is cut over
- IEIEJ p-A not landed on the new panels unless a test says the run meets the specification

### Phase 3 — Panel replacement & field termination

- **Nature of work:** Electrical installation (on-site construction)
- **Licence question:** 電気工事業 — almost certainly required
- **Window:** C+5 mo mobilise · C+6 to C+8 mo by wave
- **Depends on:** Phase 1 panels for that wave, and the Phase 2 run for that wave
- **How the delivery continues:** The same night continues into instruments and programming.

**Objective.** Physically replace the Azbil RS/RCP/CP panels with the new DDC panels and transfer every field termination, without the hotel losing conditioning.

**Scope**

- Remove 67 existing Azbil RS/RCP/CP panels, install their replacements
- Transfer and land 4,467 field terminations (3,342 binary, 534 pulse, 591 analog)
- Land each panel on the device-network run proved in Phase 2. Do not reuse IEIEJ p-A unless that test passed
- Panel power, earthing, containment and making good
- Old controller left landed on a marshalling strip for rollback

**Deliverables**

- 67 panels installed and energised
- Per-panel wiring completion certificate
- Continuity / insulation test records
- Marked-up termination drawings (as-installed)
- Rollback arrangement demonstrated per area wave

**Acceptance / completion criteria**

- "Wired" and "Terminated" signed for all 4,467 points on the commissioning checklist
- Insulation and continuity results within limits, per panel
- The panel is on the proved new run before the wave is closed

### Phase 4 — Field instrumentation replacement & calibration

- **Nature of work:** Instrumentation installation (on-site construction)
- **Licence question:** 管工事 / 電気 / 計装 — category to be confirmed
- **Window:** C+6 to C+8 mo, inside each wave after the panel is energised
- **Depends on:** Phase 3 (panel live for that area)
- **How the delivery continues:** The same night continues into the functional test.

**Objective.** Replace and calibrate the analog field devices so the new controllers read true values, which is what the optimisation sequences depend on.

**Scope**

- Replace 505 analog input devices — temperature, humidity, pressure, flow, energy
- Replace 86 analog output devices — modulating valves and damper actuators
- Verify (not replace) 534 pulse / totalizer interfaces from existing meters
- Re-range and calibrate each loop against the I/O list engineering units
- Immersion wells, averaging elements and impulse lines made good

**Deliverables**

- 591 analog devices installed
- Calibration certificate per loop, traceable
- Loop schedules marked with as-installed range and units
- 534 pulse interfaces proven for count and scaling

**Acceptance / completion criteria**

- "P2P verified" signed for all 591 analog points
- Two-point calibration recorded for every AI; stroke test for every AO
- Reading agreement against a reference instrument within tolerance

### Phase 5 — Programming, integration, tuning & handover

- **Nature of work:** Engineering / software services
- **Licence question:** 情報通信工事 — or arguably not 建設業 at all; confirm
- **Window:** C+1 mo authoring · C+5 mo head-end · C+6 mo through completion
- **Depends on:** Phase 3 and Phase 4 for that area wave. Authoring itself starts in month C+1.
- **How the delivery continues:** Closes the project at the contract date plus nine months.

**Objective.** Make the installed hardware behave: load the control logic, prove every point, tune the sequences and hand a working system to the hotel.

**Scope**

- Load and commission 109 DDC control programs (GCL+, one PG object per controller)
- Build the head-end point database and graphics for 1,383 characterised points across 259 devices
- R-1 chiller optimiser: economic dispatch, CW/CHW reset, staging, FDD
- Trend, alarm, time-program, calendar and reporting configuration
- Functional test of all 4,467 points; 24–48 h trend per panel before auto
- Seasonal tuning through first cooling season; operator training; O&M documentation

**Deliverables**

- 109 programs loaded and version-controlled
- Head-end graphics and database live on the new servers
- Functional test sheets, complete
- Trend evidence per panel
- Sequence-of-Operations compliance record against docs/control_logic.md
- Training delivered; as-built documentation issued

**Acceptance / completion criteria**

- "Func. test" signed for all 4,467 points
- Each controller demonstrated against its SOO
- 24–48 h stable trend per panel before hand-back to auto
- Operator sign-off after training

## Execution — interleaved by cutover area wave

| Wave | Area | Panels | Points | Phase 1 fabricate | Phase 2 network | Phase 3 install | Phase 4 instruments | Phase 5 program |
|---|---|---|---|---|---|---|---|---|
| 0 | Central head-end (B2F 시스템 제어반) | 1 | 25 | C+0–C+2 | proved before C+5 | C+5 | n/a | C+5 — alongside FX2 |
| 1 | Penthouse PH1/PH2 — rooftop plant, R-1, OAUs | 9 | 710 | C+0–C+3 | proved before C+6 | C+6 | C+6 | C+6 |
| 2 | Guest & public floors — 31F, 21F, 10F, 4F–1F | 26 | 2083 | C+1–C+4 | proved before C+6 | C+6–C+7 | C+6–C+7 | C+6–C+7 |
| 3 | Basements B1–B3 — plant, hydronics, DHC intake | 31 | 1649 | C+2–C+5 | proved before C+6 | C+6–C+7, last | C+6–C+7 | C+7–C+8 |
| **TOTAL** | | **67** | **4,467** | | | | | |

## Quantity reconciliation

| Quantity | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Basis |
|---|---|---|---|---|---|---|
| Panels | 67 built | — | 67 installed | — | — | panels_schedule.json |
| Controllers + modules | 904 | — | — | — | 109 programs | modTotals / functional model |
| Field points | 5,240 capacity | — | 4,467 terminated | 591 calibrated | 4,467 function-tested | usedTotal / typeTotals |
| Device network | — | survey, new cable, proved per wave | landed at cutover | — | comms proved | installed cable may be IEIEJ p-A |
| Analog devices | — | — | — | 505 AI + 86 AO | — | typeTotals |
| Pulse / totalizer | — | — | 534 landed | 534 verified | — | typeTotals |
| Checklist column | FAT record | run proved | Wired + Terminated | P2P verified | Func. test | build_commissioning.py |

## Open items — confirm before contracting

### Threshold basis (crit)

特定建設業許可 is triggered by the value a prime contractor SUBCONTRACTS OUT (4,500万円, or 7,000万円 for 建築一式工事) — not by the headline contract value. If that is the operative test, then how much the prime subcontracts matters more than how the contract is divided. DEJ is the prime. TYBMS is subcontracted to DEJ, so the test is the value DEJ places with TYBMS and any other subcontractor. Confirm with counsel against that subcontract, not against a four-way split.

### Licence category for BMS (warn)

Whether BMS work is 電気工事, 管工事, 情報通信工事 or a combination is still unresolved. It decides which phases need a licence. Phase 1 is manufacture. Phase 5 is largely services. The site exposure sits in Phase 2, Phase 3 and Phase 4.

### One delivery (info)

The proposal is one continuous project under DEJ. It is not a four-segment split, and it is not four payment contracts. A split whose only purpose is a value cap is the arrangement this plan no longer presents.

### Prime contractor identity (info)

Furukawa Denki has backed out. DEJ submits the proposal and holds the main contract. TYBMS is subcontracted to DEJ.

### Continuity of control (crit)

Phases 3, 4 and 5 run inside the same area wave. If installation finished building-wide before programming started, the hotel would sit on manual control for months. The playbook supports one panel at a time.

### Foreign personnel (info)

Scope of work permitted for Korean crews, insurance liability and safety responsibility are unresolved in writing. They bear on the on-site phases, Phase 3 and Phase 4.

