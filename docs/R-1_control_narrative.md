# R-1 Chiller — Sequence of Operations & Control Narrative

**Machine:** `R-1` — Ebara **RHS DW202M2** water-cooled *twin-screw* chiller
(エバラスクリュー冷凍機, 荏原冷熱システム, 2014-12).
**Nameplate:** 370 kW cooling / 82.2 kW input → **COP 4.50**; 2 × 45 kW screw
compressors; refrigerant **HFC-407C** (dual circuits, 28 kg × 2); 400 V-3φ-50 Hz.
**Role:** local **backup / peaking** cooling for the **36/37F** chilled-water
loop, behind the **DHC** (district) chilled-water supply.

**Ecosystem it controls:**

| Tag | Equipment | Duty |
|-----|-----------|------|
| `R-1` | Twin-screw water-cooled chiller | Backup / peak-shave source |
| `HEX-1` + `CP-8` | DHC chilled-water plate HX + primary pumps | Primary source into the 36/37F loop |
| `CHGV-1` / `CHGV-2` | Source-changeover valves | Select R-1 (branch) vs DHC (through-main) |
| `CP-7-1/2` | R-1 chilled-water pumps | Evaporator flow (duty/standby) |
| `CDP-3-1/2` | R-1 condenser-water pumps | Heat rejection flow (duty/standby) |
| `CT-3` | Cooling tower (INV fan, E/H basin heater) | Condenser heat rejection |
| `EX4` + `HP-4-1/2` + `EXT-3` | Buffer HX + secondary pumps + expansion | 36/37F secondary distribution |

> This narrative is implemented as a pure supervisory engine in
> [`backend/control.py`](../backend/control.py) and surfaced on the dashboard
> ("R-1 Chiller · Control & Optimisation"). Tariffs and setpoint envelopes at
> the top of that module are the single place to tune the strategy.

---

## 1. Source dispatch — DHC vs R-1 (economic changeover)

DHC is the **default** source. R-1 is staged **only when it is cheaper than
DHC** or needed for backup — never as base load.

Every control interval the BMS compares **marginal cost of cooling**:

- **R-1 cost** = `electricity ¥/kWh ÷ live COP`
  (electricity is time-of-use: peak `¥24/kWh` weekday 09:00–22:00, else `¥16`).
- **DHC cost** = `DHC energy ¥/kWhc` **+ DHC demand adder** during the district
  coincident-peak window (13:00–16:00) when the building is loaded.

**Decision:**

```
run R-1  when  DHC_cost > R-1_cost × 1.05   AND  36/37F loop PLR > 0.15
otherwise  supply from DHC (or Off if the loop is unloaded)
```

- Off-peak, DHC is cheaper → **DHC mode** (R-1 idle).
- During the DHC demand peak the demand adder pushes DHC above R-1 →
  **R-1 (peak-shave) mode**: R-1 runs to cap the DHC contract demand and avoid
  the demand penalty.
- A **5% margin + hysteresis** prevents hunting between the two sources.

**Changeover (`CHGV-1/2`) — bumpless transfer**

| Step | R-1 → service | R-1 → off (back to DHC) |
|------|---------------|--------------------------|
| 1 | Start `CP-7` (prove evap flow) | Ramp R-1 slide to min, stop compressors |
| 2 | Start `CDP-3` + `CT-3` (prove cond flow) | Open `CHGV-2` (DHC through-main) |
| 3 | Open `CHGV-1` (R-1 branch), close `CHGV-2` | Close `CHGV-1`; stop `CP-7`/`CDP-3`/`CT-3` after purge |
| 4 | Enable compressors on flow proof | DHC (`HEX-1`+`CP-8`) carries the loop |

Interlock: **no compressor start without both evaporator and condenser flow
proven.**

---

## 2. Condenser-water reset (largest efficiency lever)

Reset the condenser-water setpoint to track wet-bulb:

```
CW setpoint = wet-bulb + 3.5 °C,  clamped to [19 °C … 32 °C]
```

- `CT-3` fan VFD modulates to hold the setpoint; `CDP-3` staged with the chiller.
- **Floor at 19 °C** protects the R-407C **minimum lift** (expansion-valve
  differential + oil return). The panel flags "at R-407C min-lift floor" when the
  wet-bulb would drive it lower.
- Every °C of colder entering condenser water ≈ **+1.5–3 % COP** on a screw.

---

## 3. Chilled-water reset (trim-and-respond)

Loop CHW supply setpoint floats between **7 °C (design)** and **10 °C**:

- Raise the setpoint when the **most-open** 36/37F coil/FCU valve is below ~90 %
  (light load); drive back toward 7 °C as valves open up.
- Every +1 °C of CHW ≈ **+2–3 % COP**.

---

## 4. Compressor staging (twin screw)

- **One** 45 kW screw runs up to ~55 % loop PLR; **both** above.
- **Lead/lag rotates daily** (by day-of-year parity) to equalise run-hours.
- Load is **shared** across both compressors when staged (avoids deep-unloading a
  single screw, which hurts part-load efficiency and oil return).
- **Anti-short-cycle:** minimum run / minimum off timers; screws must not
  cycle rapidly (oil + motor heat). Below ~20 % PLR the panel shows the
  anti-cycle timers active.

---

## 5. Performance & diagnostics (FDD)

Live values computed from flow × ΔT and input kW:

- **Live COP**, **kW input / kW cooling**, **kW-per-RT**.
- **Evaporator & condenser approach temps** (rising approach = fouling / low flow).

Advisories raised on the dashboard:

| FDD check | Trigger | Meaning |
|-----------|---------|---------|
| Low ΔT syndrome | CHW ΔT < 3.8 °C at high load | valves/coils passing, over-pumping |
| Condenser fouling | condenser approach > 2.6 °C | tube fouling / low CW flow → clean/eddy-test |
| High lift / min-load | PLR < 0.2 | near minimum slide; anti-cycle active |
| Short-cycling | starts/hour over limit | check staging thresholds/timers |
| Oil condition | oil ΔP / analysis out of range | see maintenance schedule |

---

## 6. Backup readiness

An idle backup that won't start on the design day is the worst outcome, so:

- **Weekly exercise:** run R-1 (as lead) **Mon 10:00–10:30** to circulate oil,
  prove starting, and keep seals/charge healthy.
- **Runtime balancing:** periodically make R-1 lead so it doesn't sit cold.
- Dashboard shows *In service*, *Exercising*, or *Standby — ready*, plus days to
  the next exercise.

---

## 7. Interlocks & protection (summary)

- Evaporator + condenser **flow proof** before compressor enable.
- **Freeze protection** on CHW; low-suction / high-discharge pressure cutouts.
- Motor overload / phase protection; `CT-3` basin **E/H heater** for freeze.
- Sequenced start/stop: pumps → tower → compressors (reverse on shutdown).

---

## 8. Maintenance program

**Screw + R-407C specifics drive the plan:**

- **Oil (health gauge):** trend oil pressure/level and **oil-filter ΔP**; annual
  **oil analysis** (moisture, acidity, spectrometric wear metals).
- **Refrigerant R-407C (zeotropic, ~5–7 K glide):** charge **as liquid**; a leak
  fractionates the blend, so **recover & recharge** rather than top up. High GWP
  (~1770) and phasing down — plan a mid-life refrigerant/replacement strategy for
  a 2014 machine.
- **Condenser tubes:** clean on a fouling-trend trigger; periodic **eddy-current**
  tube testing.
- **Cooling tower `CT-3`:** water treatment (conductivity/blowdown, biocide,
  **Legionella** control), dosing & filtration, basin heater check.
- **Electrical/mechanical:** motor insulation (megger) trend, bearing
  **vibration** trend, contactor wear, discharge superheat.

---

## Priority of levers (if nothing else)

1. **Economic dispatch + DHC peak-shaving** — biggest ¥.
2. **Condenser-water wet-bulb reset** — biggest COP.
3. **CHW trim-and-respond reset.**
4. **Compressor staging + anti-cycle + runtime balancing.**
5. **Variable secondary flow (`HP-4`) DP reset.**
6. **Clean tubes + healthy oil + exercise the backup.**
