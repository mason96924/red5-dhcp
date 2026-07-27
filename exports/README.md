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

The first three are generated from the device/point model in
[`../generate_io_list.py`](../generate_io_list.py); the switchboard schedule is
transcribed from the as-built electrical drawings.

## Regenerate

```bash
cd red5-dhcp
.venv/bin/python build_exports.py       # full / lighting / electrical
.venv/bin/python build_switchboard.py   # switchboard schedule
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
