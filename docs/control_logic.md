# Red5-DHCP — control logic / Sequence of Operations

*Generated 2026-07-27 · 84 controllers · 11 panels · 1160 I/O points.*

Control strategy is consistent with the implemented engine in [`backend/control.py`](../backend/control.py) and `backend/sim.py`.

## LCP-DHC — DHC intake & hot-well panel
*B2F Machine Room · 7 controllers*

### DDC-DHC-01
**Equipment:** DHC-CHW  
**I/O:** 10 pts (AI 7 · AO 1 · BI 1 · BO 1)

- **Purpose:**
    - Primary cooling source: modulate the DHC intake so the building CHW header / thermal demand is met at minimum district energy + demand cost.
- **Control:**
    - Modulate intake control valve `DHC-CHW.CV` (feedback `DHC-CHW.CVFB`) to hold the CHW supply setpoint on `DHC-CHW.CS-T` (return `DHC-CHW.CR-T`); cap opening during the district peak window.
    - Meter thermal energy `DHC-CHW.GJ` and flow `DHC-CHW.FLW` for demand limiting; coordinate changeover with R-1 (CHGV-1/2).
- **Safeties & monitoring:**
    - High/low supply-temp and header-pressure alarms (`DHC-CHW.CS-T`, `DHC-CHW.CS-P`); low-flow / valve-fault supervision; open the valve on loss of BMS (fail-safe cooling).

### DDC-DHC-02
**Equipment:** DHC-STEAM  
**I/O:** 7 pts (AI 4 · AO 1 · BI 1 · BO 1)

- **Purpose:**
    - DHC steam intake: reduce 0.8 MPa district steam to the 0.2 MPa house header and meter mass flow + condensate return.
- **Control:**
    - PRV holds the 0.2 MPa header setpoint; meter steam mass `DHC-STEAM.MASS` and condensate hot-return `DHC-STEAM.HR-M` back to the hot-well.
    - Enable in heating season only; isolate and drain in cooling season (Apr–May off).
- **Safeties:**
    - Over-pressure relief, high-header-pressure alarm, condensate-level and trap supervision.

### DDC-DHC-03
**Equipment:** HWT-1  
**I/O:** 5 pts (AI 2 · AO 0 · BI 2 · BO 1)

- **Purpose:**
    - Hot-well / condensate tank: buffer condensate return to the district.
- **Control:**
    - Level control with makeup; high/low-level alarms.

### DDC-DHC-04
**Equipment:** HP-5-1, HP-5-2, HP-3-1  
**I/O:** 21 pts (AI 6 · AO 3 · BI 9 · BO 3)

- **Purpose:**
    - Hot-well / condensate-return pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `HP-5-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (HP-5-1, HP-5-2, HP-3-1): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the hot-well level; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-DHC-05
**Equipment:** HP-3-2  
**I/O:** 7 pts (AI 2 · AO 1 · BI 3 · BO 1)

- **Purpose:**
    - Hot-well / condensate-return pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `HP-3-2.SS`.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the hot-well level; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-DHC-06
**Equipment:** MTR-ELEC-MAIN, MTR-GAS-MAIN, MTR-WATER-MAIN  
**I/O:** 3 pts (AI 3 · AO 0 · BI 0 · BO 0)

- **Purpose:**
    - Energy metering (no control output).
- **Function:**
    - Integrate pulse/analog energy for trend, demand limiting and peak monitoring; feed the dispatch/peak-shave logic.

### DDC-DHC-07
**Equipment:** MTR-DHC-CHW, MTR-DHC-STEAM, MTR-DHC-COND  
**I/O:** 3 pts (AI 3 · AO 0 · BI 0 · BO 0)

- **Purpose:**
    - Energy metering (no control output).
- **Function:**
    - Integrate pulse/analog energy for trend, demand limiting and peak monitoring; feed the dispatch/peak-shave logic.

## LCP-CT — Cooling-tower & condenser-water panel
*Rooftop / PH · 8 controllers*

### DDC-CT-01
**Equipment:** CT-1-1, CT-1-2, CT-1  
**I/O:** 16 pts (AI 3 · AO 2 · BI 6 · BO 5)

- **Purpose:**
    - Reject condenser heat and hold the condenser-water setpoint at minimum fan energy.
- **Staging & reset:**
    - Condenser-water setpoint = wet-bulb + approach, floored for chiller min-lift.
    - INV fan cells `*.SPD` (feedback `*.SPDFB`) modulate together to hold setpoint; stage cells (CT-1-1, CT-1-2) as load rises; start/stop `*.SS`.
    - Sequence with condenser pumps + chiller; run only when the chiller/free-cooling calls.
- **Safeties & monitoring:**
    - Basin E/H heater on low temp (freeze); makeup/level & conductivity (blowdown, Legionella control); fan INV fault `*.TRIP`; run status `*.RUN`.

### DDC-CT-02
**Equipment:** CT-2-1, CT-2-2, CT-2  
**I/O:** 18 pts (AI 3 · AO 2 · BI 7 · BO 6)

- **Purpose:**
    - Reject condenser heat and hold the condenser-water setpoint at minimum fan energy.
- **Staging & reset:**
    - Condenser-water setpoint = wet-bulb + approach, floored for chiller min-lift.
    - INV fan cells `*.SPD` (feedback `*.SPDFB`) modulate together to hold setpoint; stage cells (CT-2-1, CT-2-2) as load rises; start/stop `*.SS`.
    - Sequence with condenser pumps + chiller; run only when the chiller/free-cooling calls.
- **Safeties & monitoring:**
    - Basin E/H heater on low temp (freeze); makeup/level & conductivity (blowdown, Legionella control); fan INV fault `*.TRIP`; run status `*.RUN`.

### DDC-CT-03
**Equipment:** CT-3-1, CT-3  
**I/O:** 11 pts (AI 2 · AO 1 · BI 4 · BO 4)

- **Purpose:**
    - Reject condenser heat and hold the condenser-water setpoint at minimum fan energy.
- **Staging & reset:**
    - Condenser-water setpoint = wet-bulb + approach, floored for chiller min-lift.
    - INV fan cells `*.SPD` (feedback `*.SPDFB`) modulate together to hold setpoint; stage cells (CT-3-1) as load rises; start/stop `*.SS`.
    - Sequence with condenser pumps + chiller; run only when the chiller/free-cooling calls.
- **Safeties & monitoring:**
    - Basin E/H heater on low temp (freeze); makeup/level & conductivity (blowdown, Legionella control); fan INV fault `*.TRIP`; run status `*.RUN`.

### DDC-CT-04
**Equipment:** CDP-1-1, CDP-1-2, CDP-1-3  
**I/O:** 12 pts (AI 0 · AO 0 · BI 9 · BO 3)

- **Purpose:**
    - Condenser-water pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CDP-1-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (CDP-1-1, CDP-1-2, CDP-1-3): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - Constant-speed; maintain header differential pressure via staging and the min-flow bypass.
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-CT-05
**Equipment:** CDP-2-1, CDP-2-2, CDP-3-1  
**I/O:** 12 pts (AI 0 · AO 0 · BI 9 · BO 3)

- **Purpose:**
    - Condenser-water pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CDP-2-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (CDP-2-1, CDP-2-2, CDP-3-1): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - Constant-speed; maintain header differential pressure via staging and the min-flow bypass.
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-CT-06
**Equipment:** CDP-3-2  
**I/O:** 4 pts (AI 0 · AO 0 · BI 3 · BO 1)

- **Purpose:**
    - Condenser-water pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CDP-3-2.SS`.
- **Modulation & reset:**
    - Constant-speed; maintain header differential pressure via staging and the min-flow bypass.
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-CT-07
**Equipment:** EX-1, EMHX-1, EMHX-2  
**I/O:** 9 pts (AI 3 · AO 1 · BI 0 · BO 5)

**[Winter free-cooling heat exchanger]** — EX-1
- **Purpose:**
    - Winter/shoulder free-cooling: use the cooling tower to make chilled water via the HX when wet-bulb is low enough, displacing the chiller.
- **Control:**
    - Enable when tower-approachable CHW temp < CHW setpoint; modulate the primary valve to hold the loop setpoint; hand over to/from mechanical cooling with hysteresis.
- **Safeties:**
    - Freeze protection; isolate when disabled.

**[Emergency cooling heat exchanger]** — EMHX-1, EMHX-2
- **Purpose:**
    - Transfer heat to the emergency DHC loop; hold the secondary supply temperature.
- **Control:**
    - Modulate primary control valve `*.PV` (feedback `*.PVFB`) to hold the secondary outlet setpoint `*.S-OUT` from primary inlet `*.P-IN`.
    - Lead/lag/standby across 2 exchangers (EMHX-1, EMHX-2): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Safeties:**
    - Freeze / high-temp limit on the secondary; valve-fault supervision; isolate on served-loop shutdown.

### DDC-CT-08
**Equipment:** MTR-CDW-KWH  
**I/O:** 1 pts (AI 1 · AO 0 · BI 0 · BO 0)

- **Purpose:**
    - Energy metering (no control output).
- **Function:**
    - Integrate pulse/analog energy for trend, demand limiting and peak monitoring; feed the dispatch/peak-shave logic.

## LCP-HSL — Low-rise distribution panel (低層系統)
*B2F Machine Room · 17 controllers*

### DDC-HSL-01
**Equipment:** EX-2-1, EX-2-2  
**I/O:** 8 pts (AI 6 · AO 2 · BI 0 · BO 0)

- **Purpose:**
    - Transfer heat to the tempered loop; hold the secondary supply temperature.
- **Control:**
    - Modulate primary control valve `*.PV` (feedback `*.PVFB`) to hold the secondary outlet setpoint `*.S-OUT` from primary inlet `*.P-IN`.
    - Lead/lag/standby across 2 exchangers (EX-2-1, EX-2-2): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Safeties:**
    - Freeze / high-temp limit on the secondary; valve-fault supervision; isolate on served-loop shutdown.

### DDC-HSL-02
**Equipment:** CP-1-1, CP-1-2, CP-1-3  
**I/O:** 21 pts (AI 6 · AO 3 · BI 9 · BO 3)

- **Purpose:**
    - Chilled-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CP-1-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (CP-1-1, CP-1-2, CP-1-3): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-HSL-03
**Equipment:** CP-4-1, CP-4-2, CP-5-1  
**I/O:** 21 pts (AI 6 · AO 3 · BI 9 · BO 3)

- **Purpose:**
    - Chilled-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CP-4-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (CP-4-1, CP-4-2, CP-5-1): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-HSL-04
**Equipment:** CP-5-2  
**I/O:** 7 pts (AI 2 · AO 1 · BI 3 · BO 1)

- **Purpose:**
    - Chilled-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CP-5-2.SS`.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-HSL-05
**Equipment:** HP-1-1, HP-1-2, HP-1-3  
**I/O:** 21 pts (AI 6 · AO 3 · BI 9 · BO 3)

- **Purpose:**
    - Hot-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `HP-1-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (HP-1-1, HP-1-2, HP-1-3): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-HSL-06
**Equipment:** EXT-1  
**I/O:** 3 pts (AI 1 · AO 0 · BI 2 · BO 0)

- **Purpose:**
    - Loop pressurisation / expansion set.
- **Control:**
    - Maintain fill pressure via makeup valve/pump; low-pressure & level alarms.

### DDC-HSL-07
**Equipment:** ST-1  
**I/O:** 3 pts (AI 3 · AO 0 · BI 0 · BO 0)

- **Purpose:**
    - Outdoor-air station: temper and deliver ventilation air to the loop.
- **Control:**
    - Modulate to the OA supply setpoint; enable with the served distribution; economizer-favourable in shoulder season.

### DDC-HSL-08
**Equipment:** AC-1, AC-2, AC-3  
**I/O:** 29 pts (AI 6 · AO 10 · BI 10 · BO 3)

- **Purpose:**
    - Air-handling units AC-1, AC-2, AC-3: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - Constant-volume supply fan (fixed speed).
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-HSL-09
**Equipment:** AC-4, AC-5, AC-6  
**I/O:** 34 pts (AI 9 · AO 11 · BI 11 · BO 3)

- **Purpose:**
    - Air-handling units AC-4, AC-5, AC-6: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-HSL-10
**Equipment:** AC-26  
**I/O:** 12 pts (AI 3 · AO 4 · BI 4 · BO 1)

- **Purpose:**
    - Air-handling unit AC-26: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-HSL-11
**Equipment:** FCU-L-N, FCU-L-NE, FCU-L-SE  
**I/O:** 21 pts (AI 3 · AO 6 · BI 9 · BO 3)

- **Purpose:**
    - Fan-coil zone group: maintain space temperature.
- **Control:**
    - Zone thermostat cycles fan / modulates the coil valve; batch on/off and night-setback by the schedule; status/alarm to BMS.

### DDC-HSL-12
**Equipment:** FCU-L-S, FCU-L-SW  
**I/O:** 14 pts (AI 2 · AO 4 · BI 6 · BO 2)

- **Purpose:**
    - Fan-coil zone group: maintain space temperature.
- **Control:**
    - Zone thermostat cycles fan / modulates the coil valve; batch on/off and night-setback by the schedule; status/alarm to BMS.

### DDC-HSL-13
**Equipment:** SF-6, EF-28, EF-32  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-HSL-14
**Equipment:** EF-33, EF-97, RF-7  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

**[Ventilation / exhaust fan]** — EF-33, EF-97
- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

**[Field device]** — RF-7
- **Purpose:**
    - Supervise RF-7: start/stop, status and alarm as available.

### DDC-HSL-15
**Equipment:** RF-8, RF-9  
**I/O:** 6 pts (AI 0 · AO 0 · BI 4 · BO 2)

- **Purpose:**
    - Supervise RF-8, RF-9: start/stop, status and alarm as available.

### DDC-HSL-16
**Equipment:** POOL-FP  
**I/O:** 3 pts (AI 0 · AO 0 · BI 2 · BO 1)

- **Purpose:**
    - Supervise POOL-FP: start/stop, status and alarm as available.

### DDC-HSL-17
**Equipment:** MTR-AHU-KWH  
**I/O:** 1 pts (AI 1 · AO 0 · BI 0 · BO 0)

- **Purpose:**
    - Energy metering (no control output).
- **Function:**
    - Integrate pulse/analog energy for trend, demand limiting and peak monitoring; feed the dispatch/peak-shave logic.

## LCP-HSH — High-rise distribution panel (高層系統)
*PH Machine Room · 11 controllers*

### DDC-HSH-01
**Equipment:** EX-3-1, EX-3-2  
**I/O:** 8 pts (AI 6 · AO 2 · BI 0 · BO 0)

- **Purpose:**
    - Transfer heat to the tempered loop; hold the secondary supply temperature.
- **Control:**
    - Modulate primary control valve `*.PV` (feedback `*.PVFB`) to hold the secondary outlet setpoint `*.S-OUT` from primary inlet `*.P-IN`.
    - Lead/lag/standby across 2 exchangers (EX-3-1, EX-3-2): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Safeties:**
    - Freeze / high-temp limit on the secondary; valve-fault supervision; isolate on served-loop shutdown.

### DDC-HSH-02
**Equipment:** CP-2-1, CP-2-2, CP-2-3  
**I/O:** 21 pts (AI 6 · AO 3 · BI 9 · BO 3)

- **Purpose:**
    - Chilled-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CP-2-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (CP-2-1, CP-2-2, CP-2-3): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-HSH-03
**Equipment:** CP-3-1, CP-3-2, CP-6-1  
**I/O:** 21 pts (AI 6 · AO 3 · BI 9 · BO 3)

- **Purpose:**
    - Chilled-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CP-3-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (CP-3-1, CP-3-2, CP-6-1): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-HSH-04
**Equipment:** CP-6-2  
**I/O:** 7 pts (AI 2 · AO 1 · BI 3 · BO 1)

- **Purpose:**
    - Chilled-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CP-6-2.SS`.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-HSH-05
**Equipment:** HP-2-1, HP-2-2, HP-2-3  
**I/O:** 21 pts (AI 6 · AO 3 · BI 9 · BO 3)

- **Purpose:**
    - Hot-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `HP-2-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (HP-2-1, HP-2-2, HP-2-3): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-HSH-06
**Equipment:** EXT-2  
**I/O:** 3 pts (AI 1 · AO 0 · BI 2 · BO 0)

- **Purpose:**
    - Loop pressurisation / expansion set.
- **Control:**
    - Maintain fill pressure via makeup valve/pump; low-pressure & level alarms.

### DDC-HSH-07
**Equipment:** ST-2  
**I/O:** 3 pts (AI 3 · AO 0 · BI 0 · BO 0)

- **Purpose:**
    - Outdoor-air station: temper and deliver ventilation air to the loop.
- **Control:**
    - Modulate to the OA supply setpoint; enable with the served distribution; economizer-favourable in shoulder season.

### DDC-HSH-08
**Equipment:** EVU-11, EVU-12, EVU-13  
**I/O:** 39 pts (AI 12 · AO 12 · BI 12 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-HSH-09
**Equipment:** EVU-14, EVU-15  
**I/O:** 24 pts (AI 6 · AO 8 · BI 8 · BO 2)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-HSH-10
**Equipment:** FCU-H-N, FCU-H-NE, FCU-H-SE  
**I/O:** 21 pts (AI 3 · AO 6 · BI 9 · BO 3)

- **Purpose:**
    - Fan-coil zone group: maintain space temperature.
- **Control:**
    - Zone thermostat cycles fan / modulates the coil valve; batch on/off and night-setback by the schedule; status/alarm to BMS.

### DDC-HSH-11
**Equipment:** FCU-H-S, FCU-H-SW  
**I/O:** 14 pts (AI 2 · AO 4 · BI 6 · BO 2)

- **Purpose:**
    - Fan-coil zone group: maintain space temperature.
- **Control:**
    - Zone thermostat cycles fan / modulates the coil valve; batch on/off and night-setback by the schedule; status/alarm to BMS.

## LCP-3637 — 36/37F local heat-source panel (36,37F系統)
*37F PH Machine Room · 13 controllers*

### DDC-3637-01
**Equipment:** R-1  
**I/O:** 10 pts (AI 4 · AO 1 · BI 4 · BO 1)

- **Purpose:**
    - R-1 is the local water-cooled twin-screw chiller (Ebara RHS DW202M2, 370 kW, COP 4.5) that backs up / peak-shaves the DHC supply on the 36/37F loop.
- **Economic dispatch (DHC vs R-1):**
    - DHC is the default source. Stage the chiller only when its marginal cost beats DHC by >5% or DHC is unavailable: run when `DHC_cost > R-1_cost x 1.05` and loop PLR > 0.15.
    - Enable via `R-1.SS`; trim capacity with `R-1.DMD`. During the DHC coincident-peak window the demand adder pushes DHC above R-1 -> peak-shave mode.
    - Bumpless changeover through CHGV-1/2 (branch vs through-main); no compressor start without both evaporator and condenser flow proven.
- **Capacity, staging & resets:**
    - Twin 45 kW screws: one up to ~55% loop PLR, both above; balanced load-share; anti-short-cycle min-on/off; rotate lead daily.
    - CHW reset (trim-and-respond) 7->10 C to most-open coil; hold via `R-1.CHWST` (return `R-1.CHWRT`). Condenser-water reset = wet-bulb + 3.5 C, floored at 19 C (R-407C min-lift), tracked on `R-1.CWRT` via CT-3/CDP-3.
- **Safeties, backup & monitoring:**
    - Flow-proof + freeze + hi-discharge/low-suction interlocks; trip on `R-1.TRIP`; honour `R-1.LR` (local/remote).
    - Weekly readiness exercise (Mon 10:00) when otherwise idle; live COP / kW-per-RT and evap/cond approach for FDD (low-DT, condenser fouling).

### DDC-3637-02
**Equipment:** HEX-1  
**I/O:** 7 pts (AI 6 · AO 1 · BI 0 · BO 0)

- **Purpose:**
    - Transfer heat to the tempered loop; hold the secondary supply temperature.
- **Control:**
    - Modulate primary control valve `*.PV` (feedback `*.PVFB`) to hold the secondary outlet setpoint `*.S-OUT` from primary inlet `*.P-IN`.
- **Safeties:**
    - Freeze / high-temp limit on the secondary; valve-fault supervision; isolate on served-loop shutdown.

### DDC-3637-03
**Equipment:** CP-7-1, CP-7-2, CP-8-1  
**I/O:** 21 pts (AI 6 · AO 3 · BI 9 · BO 3)

- **Purpose:**
    - Chilled-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CP-7-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 3 pumps (CP-7-1, CP-7-2, CP-8-1): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-3637-04
**Equipment:** CP-8-2, CP-8-3  
**I/O:** 14 pts (AI 4 · AO 2 · BI 6 · BO 2)

- **Purpose:**
    - Chilled-water distribution pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `CP-8-2.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 2 pumps (CP-8-2, CP-8-3): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-3637-05
**Equipment:** HP-4-1, HP-4-2  
**I/O:** 14 pts (AI 4 · AO 2 · BI 6 · BO 2)

- **Purpose:**
    - Secondary buffer-loop pumps: maintain loop flow for the served load.
- **Sequencing:**
    - Start/stop on system demand via `HP-4-1.SS`, one pump at a time with flow/Δp proof.
    - Lead/lag/standby across 2 pumps (HP-4-1, HP-4-2): stage on demand, rotate lead on equal run-hours, prove each start before staging the next.
- **Modulation & reset:**
    - VFD (`*.SPD`, feedback `*.SPDFB`) modulates to hold the header differential pressure; reset the Δp setpoint down to the most-open served valve (variable-flow).
- **Safeties & monitoring:**
    - Prove flow before loading; trip on `*.TRIP`; low-Δp / no-flow and pump-fault alarms; protect duty OR standby availability at all times.

### DDC-3637-06
**Equipment:** EX4, EXT-3  
**I/O:** 7 pts (AI 4 · AO 1 · BI 2 · BO 0)

**[Plate heat exchanger (heating/tempered loop)]** — EX4
- **Purpose:**
    - Transfer heat to the tempered loop; hold the secondary supply temperature.
- **Control:**
    - Modulate primary control valve `*.PV` (feedback `*.PVFB`) to hold the secondary outlet setpoint `*.S-OUT` from primary inlet `*.P-IN`.
- **Safeties:**
    - Freeze / high-temp limit on the secondary; valve-fault supervision; isolate on served-loop shutdown.

**[Expansion / pressurisation set]** — EXT-3
- **Purpose:**
    - Loop pressurisation / expansion set.
- **Control:**
    - Maintain fill pressure via makeup valve/pump; low-pressure & level alarms.

### DDC-3637-07
**Equipment:** CHGV-1, CHGV-2  
**I/O:** 4 pts (AI 0 · AO 0 · BI 2 · BO 2)

- **Purpose:**
    - Source-changeover valve set (R-1 branch vs DHC through-main).
- **Control:**
    - Sequenced bumpless transfer with flow proof before compressor enable; position feedback and end-switch supervision.

### DDC-3637-08
**Equipment:** AC-22, AC-23, AC-24  
**I/O:** 38 pts (AI 10 · AO 13 · BI 12 · BO 3)

- **Purpose:**
    - Air-handling units AC-22, AC-23, AC-24: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-3637-09
**Equipment:** AC-25, AC-27  
**I/O:** 26 pts (AI 7 · AO 9 · BI 8 · BO 2)

- **Purpose:**
    - Air-handling units AC-25, AC-27: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-3637-10
**Equipment:** FCU-3637  
**I/O:** 7 pts (AI 1 · AO 2 · BI 3 · BO 1)

- **Purpose:**
    - Fan-coil zone group: maintain space temperature.
- **Control:**
    - Zone thermostat cycles fan / modulates the coil valve; batch on/off and night-setback by the schedule; status/alarm to BMS.

### DDC-3637-11
**Equipment:** EF-82, EF-83, EF-84  
**I/O:** 11 pts (AI 1 · AO 1 · BI 6 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-3637-12
**Equipment:** EF-85, EF-86, EF-89  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-3637-13
**Equipment:** EF-98  
**I/O:** 3 pts (AI 0 · AO 0 · BI 2 · BO 1)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

## LCP-1F — 1F–2F air-side panel
*1F EPS/AHU Room · 3 controllers*

### DDC-1F-01
**Equipment:** AC-7  
**I/O:** 12 pts (AI 3 · AO 4 · BI 4 · BO 1)

- **Purpose:**
    - Air-handling unit AC-7: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-1F-02
**Equipment:** EVU-1, EVU-2, EVU-3  
**I/O:** 36 pts (AI 9 · AO 12 · BI 12 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-1F-03
**Equipment:** EF-41, EF-42  
**I/O:** 6 pts (AI 0 · AO 0 · BI 4 · BO 2)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

## LCP-2F — 2F air-side panel
*2F AHU Room · 4 controllers*

### DDC-2F-01
**Equipment:** AC-8, AC-9, AC-10  
**I/O:** 36 pts (AI 8 · AO 13 · BI 12 · BO 3)

- **Purpose:**
    - Air-handling units AC-8, AC-9, AC-10: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-2F-02
**Equipment:** AC-11, AC-12, AC-13  
**I/O:** 36 pts (AI 9 · AO 12 · BI 12 · BO 3)

- **Purpose:**
    - Air-handling units AC-11, AC-12, AC-13: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-2F-03
**Equipment:** EVU-4, EVU-5, EVU-6  
**I/O:** 36 pts (AI 9 · AO 12 · BI 12 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-2F-04
**Equipment:** EF-2-1, EF-46, EF-47  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

## LCP-3F — 3F air-side panel
*3F AHU Room · 4 controllers*

### DDC-3F-01
**Equipment:** AC-14, AC-15, AC-16  
**I/O:** 38 pts (AI 10 · AO 13 · BI 12 · BO 3)

- **Purpose:**
    - Air-handling units AC-14, AC-15, AC-16: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-3F-02
**Equipment:** EVU-7  
**I/O:** 12 pts (AI 3 · AO 4 · BI 4 · BO 1)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-3F-03
**Equipment:** EF-56, EF-60, EF-61  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-3F-04
**Equipment:** EF-62, EF-76, EF-77  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

## LCP-4F — 4F–5F air-side panel
*4F AHU Room · 7 controllers*

### DDC-4F-01
**Equipment:** AC-17, AC-18, AC-19  
**I/O:** 38 pts (AI 10 · AO 13 · BI 12 · BO 3)

- **Purpose:**
    - Air-handling units AC-17, AC-18, AC-19: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-4F-02
**Equipment:** AC-20, AC-21  
**I/O:** 24 pts (AI 6 · AO 8 · BI 8 · BO 2)

- **Purpose:**
    - Air-handling units AC-20, AC-21: maintain supply-air temperature and space conditions on the occupancy schedule.
- **Start / fan control:**
    - Start/stop `*.SS` on the occupancy time-program; prove `*.RUN`, alarm `*.TRIP`.
    - VFD supply fan `*.SPD` (feedback `*.SPDFB`) to duct static / demand.
- **Temperature control:**
    - Cooling coil `*.CCV` modulates to hold supply-air temp `*.SAT` (return `*.RAT`).
    - Heating coil `*.HCV` sequenced with a deadband (no simultaneous heat/cool).
    - Shoulder-season (Apr–May): drive to OA economizer / free-cooling — 100% OA, cooling coil closed — per the cutover plan.
- **Safeties & monitoring:**
    - Freeze-stat, fan-status proof, filter-DP and smoke/fire interlock (shut fan, spring-return dampers); high supply-temp alarm `*.SAT`.

### DDC-4F-03
**Equipment:** EVU-8, EVU-9, EVU-10  
**I/O:** 39 pts (AI 12 · AO 12 · BI 12 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-4F-04
**Equipment:** EF-54, EF-55, EF-57  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-4F-05
**Equipment:** EF-58, EF-59, EF-59-2  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-4F-06
**Equipment:** EF-67, EF-69, EF-70  
**I/O:** 11 pts (AI 1 · AO 1 · BI 6 · BO 3)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

### DDC-4F-07
**Equipment:** EF-71  
**I/O:** 3 pts (AI 0 · AO 0 · BI 2 · BO 1)

- **Purpose:**
    - Ventilation / exhaust: run to the occupancy schedule and IAQ demand.
- **Control:**
    - Start/stop `*.SS` on schedule; interlock with associated AHU / fire mode; prove `*.RUN`, alarm `*.TRIP`.

## LCP-PKG — Packaged-unit & refrigeration panel
*B3F–B1F EPS · 7 controllers*

### DDC-PKG-01
**Equipment:** PAC-1-1, PAC-1-2, PAC-2  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Packaged DX units (PAC-1-1, PAC-1-2, PAC-2) — several serve IT/electrical rooms and run continuously.
- **Control & monitoring:**
    - BMS enables/schedules via `*.SS` and monitors run `*.RUN` + fault `*.TRIP`; capacity is on the unit's integral DX thermostat.
    - Electrical/IT-room units are 24/7 — treat as critical (stage spare cooling before any swap).

### DDC-PKG-02
**Equipment:** PAC-3, PAC-4, PAC-5  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Packaged DX units (PAC-3, PAC-4, PAC-5) — several serve IT/electrical rooms and run continuously.
- **Control & monitoring:**
    - BMS enables/schedules via `*.SS` and monitors run `*.RUN` + fault `*.TRIP`; capacity is on the unit's integral DX thermostat.
    - Electrical/IT-room units are 24/7 — treat as critical (stage spare cooling before any swap).

### DDC-PKG-03
**Equipment:** PCU-1-1, PCU-1-2, PCU-5  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Packaged DX units (PCU-1-1, PCU-1-2, PCU-5) — several serve IT/electrical rooms and run continuously.
- **Control & monitoring:**
    - BMS enables/schedules via `*.SS` and monitors run `*.RUN` + fault `*.TRIP`; capacity is on the unit's integral DX thermostat.
    - Electrical/IT-room units are 24/7 — treat as critical (stage spare cooling before any swap).

### DDC-PKG-04
**Equipment:** PCU-6, PCU-7, PCU-8  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Packaged DX units (PCU-6, PCU-7, PCU-8) — several serve IT/electrical rooms and run continuously.
- **Control & monitoring:**
    - BMS enables/schedules via `*.SS` and monitors run `*.RUN` + fault `*.TRIP`; capacity is on the unit's integral DX thermostat.
    - Electrical/IT-room units are 24/7 — treat as critical (stage spare cooling before any swap).

### DDC-PKG-05
**Equipment:** PCU-10, PCU-11, PCU-12  
**I/O:** 9 pts (AI 0 · AO 0 · BI 6 · BO 3)

- **Purpose:**
    - Packaged DX units (PCU-10, PCU-11, PCU-12) — several serve IT/electrical rooms and run continuously.
- **Control & monitoring:**
    - BMS enables/schedules via `*.SS` and monitors run `*.RUN` + fault `*.TRIP`; capacity is on the unit's integral DX thermostat.
    - Electrical/IT-room units are 24/7 — treat as critical (stage spare cooling before any swap).

### DDC-PKG-06
**Equipment:** PCU-13, PMAC-1  
**I/O:** 6 pts (AI 0 · AO 0 · BI 4 · BO 2)

- **Purpose:**
    - Packaged DX units (PCU-13, PMAC-1) — several serve IT/electrical rooms and run continuously.
- **Control & monitoring:**
    - BMS enables/schedules via `*.SS` and monitors run `*.RUN` + fault `*.TRIP`; capacity is on the unit's integral DX thermostat.
    - Electrical/IT-room units are 24/7 — treat as critical (stage spare cooling before any swap).

### DDC-PKG-07
**Equipment:** REFR-1  
**I/O:** 7 pts (AI 0 · AO 0 · BI 7 · BO 0)

- **Purpose:**
    - Supervise REFR-1: start/stop, status and alarm as available.

## LCP-LTG — Common-area & facade lighting panel
*Distributed EPS · 3 controllers*

### DDC-LTG-01
**Equipment:** LTG-AVIATION, LTG-NEON, LTG-BALCONY-L  
**I/O:** 6 pts (AI 0 · AO 0 · BI 3 · BO 3)

- **Purpose:**
    - Common-area & facade lighting groups on time-program / astronomical clock.
- **Control:**
    - On/Off `*.CMD` by schedule (and photocell/astro for facade); status `*.ST` proof.
- **Life-safety:**
    - Aviation obstruction light: regulatory — independent circuit, dusk-to-dawn/photocell, never commanded dark; failure alarms to central.

### DDC-LTG-02
**Equipment:** LTG-BALCONY-H, LTG-CORRIDOR, LTG-LOBBY  
**I/O:** 6 pts (AI 0 · AO 0 · BI 3 · BO 3)

- **Purpose:**
    - Common-area & facade lighting groups on time-program / astronomical clock.
- **Control:**
    - On/Off `*.CMD` by schedule (and photocell/astro for facade); status `*.ST` proof.

### DDC-LTG-03
**Equipment:** LTG-SOFFIT, LTG-TENANT  
**I/O:** 4 pts (AI 0 · AO 0 · BI 2 · BO 2)

- **Purpose:**
    - Common-area & facade lighting groups on time-program / astronomical clock.
- **Control:**
    - On/Off `*.CMD` by schedule (and photocell/astro for facade); status `*.ST` proof.
