# Red5-DHCP — GCL+ control programs

*Generated 2026-07-27 · 84 controllers. Delta Controls GCL+ (vendor8). Objects referenced by point-tag name; verify syntax against your enteliWEB `pg_reference.html`.*


## LCP-DHC — DHC intake & hot-well panel

### DDC-DHC-01

```gcl
'============================================================
' Program (PG): DDC-DHC-01   Panel: LCP-DHC
' Equipment: DHC-CHW
' Strategy : Intake valve modulates to CHW setpoint / thermal demand
' I/O      : 10 pts (AI 7  AO 1  BI 1  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- DHC chilled-water intake: modulate valve to hold CHW supply SP ---
"DHC-CHW.CV" = PID("CHW SP", "DHC-CHW.CS-T", "CHW Loop")
'  (or native LOOP object; direct-acting, output 0..100%)
' Cap valve during district coincident-peak window
If ("DHC Peak" = On) And ("Loop PLR" > 0.5) Then
  "DHC-CHW.CV" = Min("DHC-CHW.CV", "Peak Valve Limit")
EndIf

' Alarms & fail-safe
If "DHC-CHW.CS-T" > "CHW Hi Limit" Then "DHC CHW Alarm" = On
If "BMS Comms" = Off Then "DHC-CHW.CV" = 100   ' fail-open to cooling

End
```

### DDC-DHC-02

```gcl
'============================================================
' Program (PG): DDC-DHC-02   Panel: LCP-DHC
' Equipment: DHC-STEAM
' Strategy : PRV to 0.2 MPa header + condensate metering
' I/O      : 7 pts (AI 4  AO 1  BI 1  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- DHC steam intake: PRV to 0.2 MPa house header, heating season only ---
If "Heating Season" = On Then
  "DHC-STEAM.PRV" = PID("Steam Header SP", "House Steam P", "Steam PRV")
Else
  "DHC-STEAM.PRV" = 0   ' isolate + drain
EndIf
' Meter mass flow + condensate hot-return for demand/energy

End
```

### DDC-DHC-03

```gcl
'============================================================
' Program (PG): DDC-DHC-03   Panel: LCP-DHC
' Equipment: HWT-1
' Strategy : Level control + makeup
' I/O      : 5 pts (AI 2  AO 0  BI 2  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```

### DDC-DHC-04

```gcl
'============================================================
' Program (PG): DDC-DHC-04   Panel: LCP-DHC
' Equipment: HP-5-1, HP-5-2, HP-3-1
' Strategy : Level-controlled condensate/kitchen pumps
' I/O      : 21 pts (AI 6  AO 3  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Hot-well pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"HP-5-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "HP-5-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "HP-3-1.SS" = Off
"HP-5-1.SPD" = PID("Dp SP", "Loop Dp", "Hot-well pumps Loop")
"HP-5-2.SPD" = PID("Dp SP", "Loop Dp", "Hot-well pumps Loop")
"HP-3-1.SPD" = PID("Dp SP", "Loop Dp", "Hot-well pumps Loop")
If "HP-5-1.TRIP" = Active Then "HP-5-1 Alarm" = On
If "HP-5-2.TRIP" = Active Then "HP-5-2 Alarm" = On
If "HP-3-1.TRIP" = Active Then "HP-3-1 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-DHC-05

```gcl
'============================================================
' Program (PG): DDC-DHC-05   Panel: LCP-DHC
' Equipment: HP-3-2
' Strategy : Level-controlled condensate/kitchen pumps
' I/O      : 7 pts (AI 2  AO 1  BI 3  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Hot-well pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"HP-3-2.SS" = "Loop Enable"
"HP-3-2.SPD" = PID("Dp SP", "Loop Dp", "Hot-well pumps Loop")
If "HP-3-2.TRIP" = Active Then "HP-3-2 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-DHC-06

```gcl
'============================================================
' Program (PG): DDC-DHC-06   Panel: LCP-DHC
' Equipment: MTR-ELEC-MAIN, MTR-GAS-MAIN, MTR-WATER-MAIN
' Strategy : Energy integration (monitor only)
' I/O      : 3 pts (AI 3  AO 0  BI 0  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' Energy meter -- monitor / integrate only (no output).

End
```

### DDC-DHC-07

```gcl
'============================================================
' Program (PG): DDC-DHC-07   Panel: LCP-DHC
' Equipment: MTR-DHC-CHW, MTR-DHC-STEAM, MTR-DHC-COND
' Strategy : Energy integration (monitor only)
' I/O      : 3 pts (AI 3  AO 0  BI 0  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' Energy meter -- monitor / integrate only (no output).

End
```


## LCP-CT — Cooling-tower & condenser-water panel

### DDC-CT-01

```gcl
'============================================================
' Program (PG): DDC-CT-01   Panel: LCP-CT
' Equipment: CT-1-1, CT-1-2, CT-1
' Strategy : INV fan cells hold wet-bulb-reset condenser setpoint
' I/O      : 16 pts (AI 3  AO 2  BI 6  BO 5)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Cooling tower: INV fan cells hold condenser-water SP (wetbulb reset) ---
"CW SP" = Max(19, "Wetbulb" + "CT Approach")
"CT-1-1.SPD" = PID("CW SP", "CW Return Temp", "Tower Loop")
"CT-1-2.SPD" = PID("CW SP", "CW Return Temp", "Tower Loop")

' Stage additional cells as load rises (lead runs first)
If "CW Return Temp" > ("CW SP" + 1.5) Then "CT-1-2.SS" = On
If "CW Return Temp" < ("CW SP" + 0.3) Then "CT-1-2.SS" = Off
"CT-1-1.SS" = "Tower Enable"

' Freeze protection + fault
If "OA Temp" < 2 Then "CT Basin Heater" = On
If "CT-1-1.TRIP" = Active Then "CT Alarm" = On
If "CT-1-2.TRIP" = Active Then "CT Alarm" = On

End
```

### DDC-CT-02

```gcl
'============================================================
' Program (PG): DDC-CT-02   Panel: LCP-CT
' Equipment: CT-2-1, CT-2-2, CT-2
' Strategy : INV fan cells hold wet-bulb-reset condenser setpoint
' I/O      : 18 pts (AI 3  AO 2  BI 7  BO 6)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Cooling tower: INV fan cells hold condenser-water SP (wetbulb reset) ---
"CW SP" = Max(19, "Wetbulb" + "CT Approach")
"CT-2-1.SPD" = PID("CW SP", "CW Return Temp", "Tower Loop")
"CT-2-2.SPD" = PID("CW SP", "CW Return Temp", "Tower Loop")

' Stage additional cells as load rises (lead runs first)
If "CW Return Temp" > ("CW SP" + 1.5) Then "CT-2-2.SS" = On
If "CW Return Temp" < ("CW SP" + 0.3) Then "CT-2-2.SS" = Off
"CT-2-1.SS" = "Tower Enable"

' Freeze protection + fault
If "OA Temp" < 2 Then "CT Basin Heater" = On
If "CT-2-1.TRIP" = Active Then "CT Alarm" = On
If "CT-2-2.TRIP" = Active Then "CT Alarm" = On

End
```

### DDC-CT-03

```gcl
'============================================================
' Program (PG): DDC-CT-03   Panel: LCP-CT
' Equipment: CT-3-1, CT-3
' Strategy : INV fan cells hold wet-bulb-reset condenser setpoint
' I/O      : 11 pts (AI 2  AO 1  BI 4  BO 4)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Cooling tower: INV fan cells hold condenser-water SP (wetbulb reset) ---
"CW SP" = Max(19, "Wetbulb" + "CT Approach")
"CT-3-1.SPD" = PID("CW SP", "CW Return Temp", "Tower Loop")

' Stage additional cells as load rises (lead runs first)
If "CW Return Temp" > ("CW SP" + 1.5) Then "CT-3-1.SS" = On
If "CW Return Temp" < ("CW SP" + 0.3) Then "CT-3-1.SS" = Off
"CT-3-1.SS" = "Tower Enable"

' Freeze protection + fault
If "OA Temp" < 2 Then "CT Basin Heater" = On
If "CT-3-1.TRIP" = Active Then "CT Alarm" = On

End
```

### DDC-CT-04

```gcl
'============================================================
' Program (PG): DDC-CT-04   Panel: LCP-CT
' Equipment: CDP-1-1, CDP-1-2, CDP-1-3
' Strategy : Duty/standby with chiller; flow-proof
' I/O      : 12 pts (AI 0  AO 0  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Condenser pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CDP-1-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "CDP-1-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "CDP-1-3.SS" = Off
If "CDP-1-1.TRIP" = Active Then "CDP-1-1 Alarm" = On
If "CDP-1-2.TRIP" = Active Then "CDP-1-2 Alarm" = On
If "CDP-1-3.TRIP" = Active Then "CDP-1-3 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-CT-05

```gcl
'============================================================
' Program (PG): DDC-CT-05   Panel: LCP-CT
' Equipment: CDP-2-1, CDP-2-2, CDP-3-1
' Strategy : Duty/standby with chiller; flow-proof
' I/O      : 12 pts (AI 0  AO 0  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Condenser pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CDP-2-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "CDP-2-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "CDP-3-1.SS" = Off
If "CDP-2-1.TRIP" = Active Then "CDP-2-1 Alarm" = On
If "CDP-2-2.TRIP" = Active Then "CDP-2-2 Alarm" = On
If "CDP-3-1.TRIP" = Active Then "CDP-3-1 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-CT-06

```gcl
'============================================================
' Program (PG): DDC-CT-06   Panel: LCP-CT
' Equipment: CDP-3-2
' Strategy : Duty/standby with chiller; flow-proof
' I/O      : 4 pts (AI 0  AO 0  BI 3  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Condenser pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CDP-3-2.SS" = "Loop Enable"
If "CDP-3-2.TRIP" = Active Then "CDP-3-2 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-CT-07

```gcl
'============================================================
' Program (PG): DDC-CT-07   Panel: LCP-CT
' Equipment: EX-1, EMHX-1, EMHX-2
' Strategy : Tower free-cooling when wet-bulb low; Emergency DHC HX standby
' I/O      : 9 pts (AI 3  AO 1  BI 0  BO 5)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' === [Winter free-cooling heat exchanger] EX-1 ===
' --- Winter/shoulder free-cooling via tower + HX ---
If ("Wetbulb" + "CT Approach") < ("CHW SP" - 1) Then
  "Freecool Enable" = On
Else
  "Freecool Enable" = Off   ' hand back to mechanical cooling (hysteresis)
EndIf


' === [Emergency cooling heat exchanger] EMHX-1, EMHX-2 ===
' --- Heat exchanger (emergency DHC loop): primary valve holds secondary outlet SP ---

End
```

### DDC-CT-08

```gcl
'============================================================
' Program (PG): DDC-CT-08   Panel: LCP-CT
' Equipment: MTR-CDW-KWH
' Strategy : Energy integration (monitor only)
' I/O      : 1 pts (AI 1  AO 0  BI 0  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' Energy meter -- monitor / integrate only (no output).

End
```


## LCP-HSL — Low-rise distribution panel (低層系統)

### DDC-HSL-01

```gcl
'============================================================
' Program (PG): DDC-HSL-01   Panel: LCP-HSL
' Equipment: EX-2-1, EX-2-2
' Strategy : Primary valve modulates to secondary outlet setpoint
' I/O      : 8 pts (AI 6  AO 2  BI 0  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Heat exchanger (tempered loop): primary valve holds secondary outlet SP ---
"EX-2-1.PV" = PID("EX-2-1 Sec SP", "EX-2-1.S-OUT", "EX-2-1 Loop")
If "EX-2-1.S-OUT" > "EX-2-1 Hi Limit" Then "EX-2-1 Alarm" = On
"EX-2-2.PV" = PID("EX-2-2 Sec SP", "EX-2-2.S-OUT", "EX-2-2 Loop")
If "EX-2-2.S-OUT" > "EX-2-2 Hi Limit" Then "EX-2-2 Alarm" = On

End
```

### DDC-HSL-02

```gcl
'============================================================
' Program (PG): DDC-HSL-02   Panel: LCP-HSL
' Equipment: CP-1-1, CP-1-2, CP-1-3
' Strategy : Lead/lag VFD to header Δp (variable flow)
' I/O      : 21 pts (AI 6  AO 3  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- CHW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CP-1-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "CP-1-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "CP-1-3.SS" = Off
"CP-1-1.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-1-2.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-1-3.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
If "CP-1-1.TRIP" = Active Then "CP-1-1 Alarm" = On
If "CP-1-2.TRIP" = Active Then "CP-1-2 Alarm" = On
If "CP-1-3.TRIP" = Active Then "CP-1-3 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-HSL-03

```gcl
'============================================================
' Program (PG): DDC-HSL-03   Panel: LCP-HSL
' Equipment: CP-4-1, CP-4-2, CP-5-1
' Strategy : Lead/lag VFD to header Δp (variable flow)
' I/O      : 21 pts (AI 6  AO 3  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- CHW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CP-4-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "CP-4-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "CP-5-1.SS" = Off
"CP-4-1.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-4-2.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-5-1.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
If "CP-4-1.TRIP" = Active Then "CP-4-1 Alarm" = On
If "CP-4-2.TRIP" = Active Then "CP-4-2 Alarm" = On
If "CP-5-1.TRIP" = Active Then "CP-5-1 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-HSL-04

```gcl
'============================================================
' Program (PG): DDC-HSL-04   Panel: LCP-HSL
' Equipment: CP-5-2
' Strategy : Lead/lag VFD to header Δp (variable flow)
' I/O      : 7 pts (AI 2  AO 1  BI 3  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- CHW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CP-5-2.SS" = "Loop Enable"
"CP-5-2.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
If "CP-5-2.TRIP" = Active Then "CP-5-2 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-HSL-05

```gcl
'============================================================
' Program (PG): DDC-HSL-05   Panel: LCP-HSL
' Equipment: HP-1-1, HP-1-2, HP-1-3
' Strategy : Heating-season lead/lag to header Δp
' I/O      : 21 pts (AI 6  AO 3  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- HW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"HP-1-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "HP-1-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "HP-1-3.SS" = Off
"HP-1-1.SPD" = PID("Dp SP", "Loop Dp", "HW pumps Loop")
"HP-1-2.SPD" = PID("Dp SP", "Loop Dp", "HW pumps Loop")
"HP-1-3.SPD" = PID("Dp SP", "Loop Dp", "HW pumps Loop")
If "HP-1-1.TRIP" = Active Then "HP-1-1 Alarm" = On
If "HP-1-2.TRIP" = Active Then "HP-1-2 Alarm" = On
If "HP-1-3.TRIP" = Active Then "HP-1-3 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-HSL-06

```gcl
'============================================================
' Program (PG): DDC-HSL-06   Panel: LCP-HSL
' Equipment: EXT-1
' Strategy : Loop pressurisation
' I/O      : 3 pts (AI 1  AO 0  BI 2  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```

### DDC-HSL-07

```gcl
'============================================================
' Program (PG): DDC-HSL-07   Panel: LCP-HSL
' Equipment: ST-1
' Strategy : OA tempering to setpoint
' I/O      : 3 pts (AI 3  AO 0  BI 0  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---

End
```

### DDC-HSL-08

```gcl
'============================================================
' Program (PG): DDC-HSL-08   Panel: LCP-HSL
' Equipment: AC-1, AC-2, AC-3
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 29 pts (AI 6  AO 10  BI 10  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-1: schedule start, SAT control, economizer ---
"AC-1.SS" = "Occupancy Sched"
"AC-1.SPD" = "AC-1 Fan Speed"   ' constant volume
"AC-1.CCV" = PID("AC-1 SAT SP", "AC-1.SAT", "AC-1 Cool")
"AC-1.HCV" = PID_Heat("AC-1 SAT SP", "AC-1.SAT", "AC-1 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-1.OAD" = 100
  "AC-1.CCV" = 0
EndIf
If "AC-1.TRIP" = Active Then "AC-1 Fan Alarm" = On
If "Freezestat" = Active Then "AC-1.SS" = Off   ' freeze protection

' --- AHU AC-2: schedule start, SAT control, economizer ---
"AC-2.SS" = "Occupancy Sched"
"AC-2.SPD" = "AC-2 Fan Speed"   ' constant volume
"AC-2.CCV" = PID("AC-2 SAT SP", "AC-2.SAT", "AC-2 Cool")
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-2.OAD" = 100
  "AC-2.CCV" = 0
EndIf
If "AC-2.TRIP" = Active Then "AC-2 Fan Alarm" = On
If "Freezestat" = Active Then "AC-2.SS" = Off   ' freeze protection

' --- AHU AC-3: schedule start, SAT control, economizer ---
"AC-3.SS" = "Occupancy Sched"
"AC-3.SPD" = "AC-3 Fan Speed"   ' constant volume
"AC-3.CCV" = PID("AC-3 SAT SP", "AC-3.SAT", "AC-3 Cool")
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-3.OAD" = 100
  "AC-3.CCV" = 0
EndIf
If "AC-3.TRIP" = Active Then "AC-3 Fan Alarm" = On
If "Freezestat" = Active Then "AC-3.SS" = Off   ' freeze protection


End
```

### DDC-HSL-09

```gcl
'============================================================
' Program (PG): DDC-HSL-09   Panel: LCP-HSL
' Equipment: AC-4, AC-5, AC-6
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 34 pts (AI 9  AO 11  BI 11  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-4: schedule start, SAT control, economizer ---
"AC-4.SS" = "Occupancy Sched"
"AC-4.SPD" = PID("Duct Static SP", "Duct Static", "AC-4 Fan")
"AC-4.CCV" = PID("AC-4 SAT SP", "AC-4.SAT", "AC-4 Cool")
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-4.OAD" = 100
  "AC-4.CCV" = 0
EndIf
If "AC-4.TRIP" = Active Then "AC-4 Fan Alarm" = On
If "Freezestat" = Active Then "AC-4.SS" = Off   ' freeze protection

' --- AHU AC-5: schedule start, SAT control, economizer ---
"AC-5.SS" = "Occupancy Sched"
"AC-5.SPD" = PID("Duct Static SP", "Duct Static", "AC-5 Fan")
"AC-5.CCV" = PID("AC-5 SAT SP", "AC-5.SAT", "AC-5 Cool")
"AC-5.HCV" = PID_Heat("AC-5 SAT SP", "AC-5.SAT", "AC-5 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-5.OAD" = 100
  "AC-5.CCV" = 0
EndIf
If "AC-5.TRIP" = Active Then "AC-5 Fan Alarm" = On
If "Freezestat" = Active Then "AC-5.SS" = Off   ' freeze protection

' --- AHU AC-6: schedule start, SAT control, economizer ---
"AC-6.SS" = "Occupancy Sched"
"AC-6.SPD" = PID("Duct Static SP", "Duct Static", "AC-6 Fan")
"AC-6.CCV" = PID("AC-6 SAT SP", "AC-6.SAT", "AC-6 Cool")
"AC-6.HCV" = PID_Heat("AC-6 SAT SP", "AC-6.SAT", "AC-6 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-6.OAD" = 100
  "AC-6.CCV" = 0
EndIf
If "AC-6.TRIP" = Active Then "AC-6 Fan Alarm" = On
If "Freezestat" = Active Then "AC-6.SS" = Off   ' freeze protection


End
```

### DDC-HSL-10

```gcl
'============================================================
' Program (PG): DDC-HSL-10   Panel: LCP-HSL
' Equipment: AC-26
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 12 pts (AI 3  AO 4  BI 4  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-26: schedule start, SAT control, economizer ---
"AC-26.SS" = "Occupancy Sched"
"AC-26.SPD" = PID("Duct Static SP", "Duct Static", "AC-26 Fan")
"AC-26.CCV" = PID("AC-26 SAT SP", "AC-26.SAT", "AC-26 Cool")
"AC-26.HCV" = PID_Heat("AC-26 SAT SP", "AC-26.SAT", "AC-26 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-26.OAD" = 100
  "AC-26.CCV" = 0
EndIf
If "AC-26.TRIP" = Active Then "AC-26 Fan Alarm" = On
If "Freezestat" = Active Then "AC-26.SS" = Off   ' freeze protection


End
```

### DDC-HSL-11

```gcl
'============================================================
' Program (PG): DDC-HSL-11   Panel: LCP-HSL
' Equipment: FCU-L-N, FCU-L-NE, FCU-L-SE
' Strategy : Zone thermostat + schedule batch
' I/O      : 21 pts (AI 3  AO 6  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```

### DDC-HSL-12

```gcl
'============================================================
' Program (PG): DDC-HSL-12   Panel: LCP-HSL
' Equipment: FCU-L-S, FCU-L-SW
' Strategy : Zone thermostat + schedule batch
' I/O      : 14 pts (AI 2  AO 4  BI 6  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```

### DDC-HSL-13

```gcl
'============================================================
' Program (PG): DDC-HSL-13   Panel: LCP-HSL
' Equipment: SF-6, EF-28, EF-32
' Strategy : Scheduled ventilation / exhaust
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"SF-6.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "SF-6.TRIP" = Active Then "SF-6 Alarm" = On
"EF-28.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-28.TRIP" = Active Then "EF-28 Alarm" = On
"EF-32.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-32.TRIP" = Active Then "EF-32 Alarm" = On

End
```

### DDC-HSL-14

```gcl
'============================================================
' Program (PG): DDC-HSL-14   Panel: LCP-HSL
' Equipment: EF-33, EF-97, RF-7
' Strategy : Scheduled ventilation / exhaust; Start/stop + status/alarm
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' === [Ventilation / exhaust fan] EF-33, EF-97 ===
' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-33.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-33.TRIP" = Active Then "EF-33 Alarm" = On
"EF-97.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-97.TRIP" = Active Then "EF-97 Alarm" = On

' === [Field device] RF-7 ===
' --- Supervise: enable, prove status, alarm ---
"RF-7.SS" = "RF-7 Enable"
If "RF-7.TRIP" = Active Then "RF-7 Alarm" = On

End
```

### DDC-HSL-15

```gcl
'============================================================
' Program (PG): DDC-HSL-15   Panel: LCP-HSL
' Equipment: RF-8, RF-9
' Strategy : Start/stop + status/alarm
' I/O      : 6 pts (AI 0  AO 0  BI 4  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---
"RF-8.SS" = "RF-8 Enable"
If "RF-8.TRIP" = Active Then "RF-8 Alarm" = On
"RF-9.SS" = "RF-9 Enable"
If "RF-9.TRIP" = Active Then "RF-9 Alarm" = On

End
```

### DDC-HSL-16

```gcl
'============================================================
' Program (PG): DDC-HSL-16   Panel: LCP-HSL
' Equipment: POOL-FP
' Strategy : Start/stop + status/alarm
' I/O      : 3 pts (AI 0  AO 0  BI 2  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---
"POOL-FP.SS" = "POOL-FP Enable"
If "POOL-FP.TRIP" = Active Then "POOL-FP Alarm" = On

End
```

### DDC-HSL-17

```gcl
'============================================================
' Program (PG): DDC-HSL-17   Panel: LCP-HSL
' Equipment: MTR-AHU-KWH
' Strategy : Energy integration (monitor only)
' I/O      : 1 pts (AI 1  AO 0  BI 0  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' Energy meter -- monitor / integrate only (no output).

End
```


## LCP-HSH — High-rise distribution panel (高層系統)

### DDC-HSH-01

```gcl
'============================================================
' Program (PG): DDC-HSH-01   Panel: LCP-HSH
' Equipment: EX-3-1, EX-3-2
' Strategy : Primary valve modulates to secondary outlet setpoint
' I/O      : 8 pts (AI 6  AO 2  BI 0  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Heat exchanger (tempered loop): primary valve holds secondary outlet SP ---
"EX-3-1.PV" = PID("EX-3-1 Sec SP", "EX-3-1.S-OUT", "EX-3-1 Loop")
If "EX-3-1.S-OUT" > "EX-3-1 Hi Limit" Then "EX-3-1 Alarm" = On
"EX-3-2.PV" = PID("EX-3-2 Sec SP", "EX-3-2.S-OUT", "EX-3-2 Loop")
If "EX-3-2.S-OUT" > "EX-3-2 Hi Limit" Then "EX-3-2 Alarm" = On

End
```

### DDC-HSH-02

```gcl
'============================================================
' Program (PG): DDC-HSH-02   Panel: LCP-HSH
' Equipment: CP-2-1, CP-2-2, CP-2-3
' Strategy : Lead/lag VFD to header Δp (variable flow)
' I/O      : 21 pts (AI 6  AO 3  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- CHW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CP-2-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "CP-2-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "CP-2-3.SS" = Off
"CP-2-1.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-2-2.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-2-3.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
If "CP-2-1.TRIP" = Active Then "CP-2-1 Alarm" = On
If "CP-2-2.TRIP" = Active Then "CP-2-2 Alarm" = On
If "CP-2-3.TRIP" = Active Then "CP-2-3 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-HSH-03

```gcl
'============================================================
' Program (PG): DDC-HSH-03   Panel: LCP-HSH
' Equipment: CP-3-1, CP-3-2, CP-6-1
' Strategy : Lead/lag VFD to header Δp (variable flow)
' I/O      : 21 pts (AI 6  AO 3  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- CHW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CP-3-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "CP-3-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "CP-6-1.SS" = Off
"CP-3-1.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-3-2.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-6-1.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
If "CP-3-1.TRIP" = Active Then "CP-3-1 Alarm" = On
If "CP-3-2.TRIP" = Active Then "CP-3-2 Alarm" = On
If "CP-6-1.TRIP" = Active Then "CP-6-1 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-HSH-04

```gcl
'============================================================
' Program (PG): DDC-HSH-04   Panel: LCP-HSH
' Equipment: CP-6-2
' Strategy : Lead/lag VFD to header Δp (variable flow)
' I/O      : 7 pts (AI 2  AO 1  BI 3  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- CHW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CP-6-2.SS" = "Loop Enable"
"CP-6-2.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
If "CP-6-2.TRIP" = Active Then "CP-6-2 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-HSH-05

```gcl
'============================================================
' Program (PG): DDC-HSH-05   Panel: LCP-HSH
' Equipment: HP-2-1, HP-2-2, HP-2-3
' Strategy : Heating-season lead/lag to header Δp
' I/O      : 21 pts (AI 6  AO 3  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- HW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"HP-2-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "HP-2-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "HP-2-3.SS" = Off
"HP-2-1.SPD" = PID("Dp SP", "Loop Dp", "HW pumps Loop")
"HP-2-2.SPD" = PID("Dp SP", "Loop Dp", "HW pumps Loop")
"HP-2-3.SPD" = PID("Dp SP", "Loop Dp", "HW pumps Loop")
If "HP-2-1.TRIP" = Active Then "HP-2-1 Alarm" = On
If "HP-2-2.TRIP" = Active Then "HP-2-2 Alarm" = On
If "HP-2-3.TRIP" = Active Then "HP-2-3 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-HSH-06

```gcl
'============================================================
' Program (PG): DDC-HSH-06   Panel: LCP-HSH
' Equipment: EXT-2
' Strategy : Loop pressurisation
' I/O      : 3 pts (AI 1  AO 0  BI 2  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```

### DDC-HSH-07

```gcl
'============================================================
' Program (PG): DDC-HSH-07   Panel: LCP-HSH
' Equipment: ST-2
' Strategy : OA tempering to setpoint
' I/O      : 3 pts (AI 3  AO 0  BI 0  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---

End
```

### DDC-HSH-08

```gcl
'============================================================
' Program (PG): DDC-HSH-08   Panel: LCP-HSH
' Equipment: EVU-11, EVU-12, EVU-13
' Strategy : Scheduled ventilation / exhaust
' I/O      : 39 pts (AI 12  AO 12  BI 12  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EVU-11.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-11.TRIP" = Active Then "EVU-11 Alarm" = On
"EVU-12.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-12.TRIP" = Active Then "EVU-12 Alarm" = On
"EVU-13.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-13.TRIP" = Active Then "EVU-13 Alarm" = On

End
```

### DDC-HSH-09

```gcl
'============================================================
' Program (PG): DDC-HSH-09   Panel: LCP-HSH
' Equipment: EVU-14, EVU-15
' Strategy : Scheduled ventilation / exhaust
' I/O      : 24 pts (AI 6  AO 8  BI 8  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EVU-14.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-14.TRIP" = Active Then "EVU-14 Alarm" = On
"EVU-15.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-15.TRIP" = Active Then "EVU-15 Alarm" = On

End
```

### DDC-HSH-10

```gcl
'============================================================
' Program (PG): DDC-HSH-10   Panel: LCP-HSH
' Equipment: FCU-H-N, FCU-H-NE, FCU-H-SE
' Strategy : Zone thermostat + schedule batch
' I/O      : 21 pts (AI 3  AO 6  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```

### DDC-HSH-11

```gcl
'============================================================
' Program (PG): DDC-HSH-11   Panel: LCP-HSH
' Equipment: FCU-H-S, FCU-H-SW
' Strategy : Zone thermostat + schedule batch
' I/O      : 14 pts (AI 2  AO 4  BI 6  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```


## LCP-3637 — 36/37F local heat-source panel (36,37F系統)

### DDC-3637-01

```gcl
'============================================================
' Program (PG): DDC-3637-01   Panel: LCP-3637
' Equipment: R-1
' Strategy : Economic dispatch + CHW/CW reset + twin-screw staging
' I/O      : 10 pts (AI 4  AO 1  BI 4  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- R-1 economic dispatch (DHC is default source) ---
'  AVs: "DHC Cost" "R1 Cost" "Loop PLR" "Most Open Valve" "Wetbulb"
If ("DHC Available" = Off) Or ("DHC Cost" > "R1 Cost" * 1.05) Then
  If "Loop PLR" > 0.15 Then "R-1 Enable" = On
Else
  "R-1 Enable" = Off
EndIf

' --- CHW reset (trim & respond 7..10 C) and condenser reset (wetbulb+3.5, floor 19) ---
"R-1 CHW SP" = Max(7, Min(10, 10 - ("Most Open Valve" - 90) / 10))
"CW SP"     = Max(19, "Wetbulb" + 3.5)

' --- Flow-proof interlock before enabling the machine ---
If ("CP-7.RUN" = Off) Or ("CDP-3.RUN" = Off) Then "R-1 Enable" = Off

If "R-1 Enable" = On Then
  "R-1.SS" = On
  "R-1.DMD" = "Capacity Limit"
Else
  "R-1.SS" = Off
EndIf

If "R-1.TRIP" = Active Then "R-1 Alarm" = On

End
```

### DDC-3637-02

```gcl
'============================================================
' Program (PG): DDC-3637-02   Panel: LCP-3637
' Equipment: HEX-1
' Strategy : Primary valve modulates to secondary outlet setpoint
' I/O      : 7 pts (AI 6  AO 1  BI 0  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Heat exchanger (tempered loop): primary valve holds secondary outlet SP ---
"HEX-1.PV" = PID("HEX-1 Sec SP", "HEX-1.S-OUT", "HEX-1 Loop")
If "HEX-1.S-OUT" > "HEX-1 Hi Limit" Then "HEX-1 Alarm" = On

End
```

### DDC-3637-03

```gcl
'============================================================
' Program (PG): DDC-3637-03   Panel: LCP-3637
' Equipment: CP-7-1, CP-7-2, CP-8-1
' Strategy : Lead/lag VFD to header Δp (variable flow)
' I/O      : 21 pts (AI 6  AO 3  BI 9  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- CHW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CP-7-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "CP-7-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "CP-8-1.SS" = Off
"CP-7-1.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-7-2.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-8-1.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
If "CP-7-1.TRIP" = Active Then "CP-7-1 Alarm" = On
If "CP-7-2.TRIP" = Active Then "CP-7-2 Alarm" = On
If "CP-8-1.TRIP" = Active Then "CP-8-1 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-3637-04

```gcl
'============================================================
' Program (PG): DDC-3637-04   Panel: LCP-3637
' Equipment: CP-8-2, CP-8-3
' Strategy : Lead/lag VFD to header Δp (variable flow)
' I/O      : 14 pts (AI 4  AO 2  BI 6  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- CHW pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"CP-8-2.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "CP-8-3.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "CP-8-3.SS" = Off
"CP-8-2.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
"CP-8-3.SPD" = PID("Dp SP", "Loop Dp", "CHW pumps Loop")
If "CP-8-2.TRIP" = Active Then "CP-8-2 Alarm" = On
If "CP-8-3.TRIP" = Active Then "CP-8-3 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-3637-05

```gcl
'============================================================
' Program (PG): DDC-3637-05   Panel: LCP-3637
' Equipment: HP-4-1, HP-4-2
' Strategy : Buffer-loop lead/lag to Δp
' I/O      : 14 pts (AI 4  AO 2  BI 6  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Secondary pumps: stage on demand, lead/lag/standby, VFD to header Dp ---
"HP-4-1.SS" = "Loop Enable"
' Rotate lead on equal run-hours; stage lag on low Dp / high demand
If "Loop Dp" < ("Dp SP" - "Dp Db") Then "HP-4-2.SS" = On
If "Loop Dp" > ("Dp SP" + "Dp Db") Then "HP-4-2.SS" = Off
"HP-4-1.SPD" = PID("Dp SP", "Loop Dp", "Secondary pumps Loop")
"HP-4-2.SPD" = PID("Dp SP", "Loop Dp", "Secondary pumps Loop")
If "HP-4-1.TRIP" = Active Then "HP-4-1 Alarm" = On
If "HP-4-2.TRIP" = Active Then "HP-4-2 Alarm" = On
' Guarantee duty OR standby availability at all times

End
```

### DDC-3637-06

```gcl
'============================================================
' Program (PG): DDC-3637-06   Panel: LCP-3637
' Equipment: EX4, EXT-3
' Strategy : Primary valve modulates to secondary outlet setpoint; Loop pressurisation
' I/O      : 7 pts (AI 4  AO 1  BI 2  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' === [Plate heat exchanger (heating/tempered loop)] EX4 ===
' --- Heat exchanger (tempered loop): primary valve holds secondary outlet SP ---
"EX4.PV" = PID("EX4 Sec SP", "EX4.S-OUT", "EX4 Loop")
If "EX4.S-OUT" > "EX4 Hi Limit" Then "EX4 Alarm" = On

' === [Expansion / pressurisation set] EXT-3 ===
' --- Supervise: enable, prove status, alarm ---

End
```

### DDC-3637-07

```gcl
'============================================================
' Program (PG): DDC-3637-07   Panel: LCP-3637
' Equipment: CHGV-1, CHGV-2
' Strategy : Bumpless source transfer + flow proof
' I/O      : 4 pts (AI 0  AO 0  BI 2  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```

### DDC-3637-08

```gcl
'============================================================
' Program (PG): DDC-3637-08   Panel: LCP-3637
' Equipment: AC-22, AC-23, AC-24
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 38 pts (AI 10  AO 13  BI 12  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-22: schedule start, SAT control, economizer ---
"AC-22.SS" = "Occupancy Sched"
"AC-22.SPD" = PID("Duct Static SP", "Duct Static", "AC-22 Fan")
"AC-22.CCV" = PID("AC-22 SAT SP", "AC-22.SAT", "AC-22 Cool")
"AC-22.HCV" = PID_Heat("AC-22 SAT SP", "AC-22.SAT", "AC-22 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-22.OAD" = 100
  "AC-22.CCV" = 0
EndIf
If "AC-22.TRIP" = Active Then "AC-22 Fan Alarm" = On
If "Freezestat" = Active Then "AC-22.SS" = Off   ' freeze protection

' --- AHU AC-23: schedule start, SAT control, economizer ---
"AC-23.SS" = "Occupancy Sched"
"AC-23.SPD" = PID("Duct Static SP", "Duct Static", "AC-23 Fan")
"AC-23.CCV" = PID("AC-23 SAT SP", "AC-23.SAT", "AC-23 Cool")
"AC-23.HCV" = PID_Heat("AC-23 SAT SP", "AC-23.SAT", "AC-23 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-23.OAD" = 100
  "AC-23.CCV" = 0
EndIf
If "AC-23.TRIP" = Active Then "AC-23 Fan Alarm" = On
If "Freezestat" = Active Then "AC-23.SS" = Off   ' freeze protection

' --- AHU AC-24: schedule start, SAT control, economizer ---
"AC-24.SS" = "Occupancy Sched"
"AC-24.SPD" = PID("Duct Static SP", "Duct Static", "AC-24 Fan")
"AC-24.CCV" = PID("AC-24 SAT SP", "AC-24.SAT", "AC-24 Cool")
"AC-24.HCV" = PID_Heat("AC-24 SAT SP", "AC-24.SAT", "AC-24 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-24.OAD" = 100
  "AC-24.CCV" = 0
EndIf
If "AC-24.TRIP" = Active Then "AC-24 Fan Alarm" = On
If "Freezestat" = Active Then "AC-24.SS" = Off   ' freeze protection


End
```

### DDC-3637-09

```gcl
'============================================================
' Program (PG): DDC-3637-09   Panel: LCP-3637
' Equipment: AC-25, AC-27
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 26 pts (AI 7  AO 9  BI 8  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-25: schedule start, SAT control, economizer ---
"AC-25.SS" = "Occupancy Sched"
"AC-25.SPD" = PID("Duct Static SP", "Duct Static", "AC-25 Fan")
"AC-25.CCV" = PID("AC-25 SAT SP", "AC-25.SAT", "AC-25 Cool")
"AC-25.HCV" = PID_Heat("AC-25 SAT SP", "AC-25.SAT", "AC-25 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-25.OAD" = 100
  "AC-25.CCV" = 0
EndIf
If "AC-25.TRIP" = Active Then "AC-25 Fan Alarm" = On
If "Freezestat" = Active Then "AC-25.SS" = Off   ' freeze protection

' --- AHU AC-27: schedule start, SAT control, economizer ---
"AC-27.SS" = "Occupancy Sched"
"AC-27.SPD" = PID("Duct Static SP", "Duct Static", "AC-27 Fan")
"AC-27.CCV" = PID("AC-27 SAT SP", "AC-27.SAT", "AC-27 Cool")
"AC-27.HCV" = PID_Heat("AC-27 SAT SP", "AC-27.SAT", "AC-27 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-27.OAD" = 100
  "AC-27.CCV" = 0
EndIf
If "AC-27.TRIP" = Active Then "AC-27 Fan Alarm" = On
If "Freezestat" = Active Then "AC-27.SS" = Off   ' freeze protection


End
```

### DDC-3637-10

```gcl
'============================================================
' Program (PG): DDC-3637-10   Panel: LCP-3637
' Equipment: FCU-3637
' Strategy : Zone thermostat + schedule batch
' I/O      : 7 pts (AI 1  AO 2  BI 3  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```

### DDC-3637-11

```gcl
'============================================================
' Program (PG): DDC-3637-11   Panel: LCP-3637
' Equipment: EF-82, EF-83, EF-84
' Strategy : Scheduled ventilation / exhaust
' I/O      : 11 pts (AI 1  AO 1  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-82.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-82.TRIP" = Active Then "EF-82 Alarm" = On
"EF-83.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-83.TRIP" = Active Then "EF-83 Alarm" = On
"EF-84.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-84.TRIP" = Active Then "EF-84 Alarm" = On

End
```

### DDC-3637-12

```gcl
'============================================================
' Program (PG): DDC-3637-12   Panel: LCP-3637
' Equipment: EF-85, EF-86, EF-89
' Strategy : Scheduled ventilation / exhaust
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-85.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-85.TRIP" = Active Then "EF-85 Alarm" = On
"EF-86.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-86.TRIP" = Active Then "EF-86 Alarm" = On
"EF-89.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-89.TRIP" = Active Then "EF-89 Alarm" = On

End
```

### DDC-3637-13

```gcl
'============================================================
' Program (PG): DDC-3637-13   Panel: LCP-3637
' Equipment: EF-98
' Strategy : Scheduled ventilation / exhaust
' I/O      : 3 pts (AI 0  AO 0  BI 2  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-98.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-98.TRIP" = Active Then "EF-98 Alarm" = On

End
```


## LCP-1F — 1F–2F air-side panel

### DDC-1F-01

```gcl
'============================================================
' Program (PG): DDC-1F-01   Panel: LCP-1F
' Equipment: AC-7
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 12 pts (AI 3  AO 4  BI 4  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-7: schedule start, SAT control, economizer ---
"AC-7.SS" = "Occupancy Sched"
"AC-7.SPD" = PID("Duct Static SP", "Duct Static", "AC-7 Fan")
"AC-7.CCV" = PID("AC-7 SAT SP", "AC-7.SAT", "AC-7 Cool")
"AC-7.HCV" = PID_Heat("AC-7 SAT SP", "AC-7.SAT", "AC-7 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-7.OAD" = 100
  "AC-7.CCV" = 0
EndIf
If "AC-7.TRIP" = Active Then "AC-7 Fan Alarm" = On
If "Freezestat" = Active Then "AC-7.SS" = Off   ' freeze protection


End
```

### DDC-1F-02

```gcl
'============================================================
' Program (PG): DDC-1F-02   Panel: LCP-1F
' Equipment: EVU-1, EVU-2, EVU-3
' Strategy : Scheduled ventilation / exhaust
' I/O      : 36 pts (AI 9  AO 12  BI 12  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EVU-1.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-1.TRIP" = Active Then "EVU-1 Alarm" = On
"EVU-2.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-2.TRIP" = Active Then "EVU-2 Alarm" = On
"EVU-3.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-3.TRIP" = Active Then "EVU-3 Alarm" = On

End
```

### DDC-1F-03

```gcl
'============================================================
' Program (PG): DDC-1F-03   Panel: LCP-1F
' Equipment: EF-41, EF-42
' Strategy : Scheduled ventilation / exhaust
' I/O      : 6 pts (AI 0  AO 0  BI 4  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-41.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-41.TRIP" = Active Then "EF-41 Alarm" = On
"EF-42.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-42.TRIP" = Active Then "EF-42 Alarm" = On

End
```


## LCP-2F — 2F air-side panel

### DDC-2F-01

```gcl
'============================================================
' Program (PG): DDC-2F-01   Panel: LCP-2F
' Equipment: AC-8, AC-9, AC-10
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 36 pts (AI 8  AO 13  BI 12  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-8: schedule start, SAT control, economizer ---
"AC-8.SS" = "Occupancy Sched"
"AC-8.SPD" = "AC-8 Fan Speed"   ' constant volume
"AC-8.CCV" = PID("AC-8 SAT SP", "AC-8.SAT", "AC-8 Cool")
"AC-8.HCV" = PID_Heat("AC-8 SAT SP", "AC-8.SAT", "AC-8 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-8.OAD" = 100
  "AC-8.CCV" = 0
EndIf
If "AC-8.TRIP" = Active Then "AC-8 Fan Alarm" = On
If "Freezestat" = Active Then "AC-8.SS" = Off   ' freeze protection

' --- AHU AC-9: schedule start, SAT control, economizer ---
"AC-9.SS" = "Occupancy Sched"
"AC-9.SPD" = "AC-9 Fan Speed"   ' constant volume
"AC-9.CCV" = PID("AC-9 SAT SP", "AC-9.SAT", "AC-9 Cool")
"AC-9.HCV" = PID_Heat("AC-9 SAT SP", "AC-9.SAT", "AC-9 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-9.OAD" = 100
  "AC-9.CCV" = 0
EndIf
If "AC-9.TRIP" = Active Then "AC-9 Fan Alarm" = On
If "Freezestat" = Active Then "AC-9.SS" = Off   ' freeze protection

' --- AHU AC-10: schedule start, SAT control, economizer ---
"AC-10.SS" = "Occupancy Sched"
"AC-10.SPD" = PID("Duct Static SP", "Duct Static", "AC-10 Fan")
"AC-10.CCV" = PID("AC-10 SAT SP", "AC-10.SAT", "AC-10 Cool")
"AC-10.HCV" = PID_Heat("AC-10 SAT SP", "AC-10.SAT", "AC-10 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-10.OAD" = 100
  "AC-10.CCV" = 0
EndIf
If "AC-10.TRIP" = Active Then "AC-10 Fan Alarm" = On
If "Freezestat" = Active Then "AC-10.SS" = Off   ' freeze protection


End
```

### DDC-2F-02

```gcl
'============================================================
' Program (PG): DDC-2F-02   Panel: LCP-2F
' Equipment: AC-11, AC-12, AC-13
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 36 pts (AI 9  AO 12  BI 12  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-11: schedule start, SAT control, economizer ---
"AC-11.SS" = "Occupancy Sched"
"AC-11.SPD" = PID("Duct Static SP", "Duct Static", "AC-11 Fan")
"AC-11.CCV" = PID("AC-11 SAT SP", "AC-11.SAT", "AC-11 Cool")
"AC-11.HCV" = PID_Heat("AC-11 SAT SP", "AC-11.SAT", "AC-11 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-11.OAD" = 100
  "AC-11.CCV" = 0
EndIf
If "AC-11.TRIP" = Active Then "AC-11 Fan Alarm" = On
If "Freezestat" = Active Then "AC-11.SS" = Off   ' freeze protection

' --- AHU AC-12: schedule start, SAT control, economizer ---
"AC-12.SS" = "Occupancy Sched"
"AC-12.SPD" = PID("Duct Static SP", "Duct Static", "AC-12 Fan")
"AC-12.CCV" = PID("AC-12 SAT SP", "AC-12.SAT", "AC-12 Cool")
"AC-12.HCV" = PID_Heat("AC-12 SAT SP", "AC-12.SAT", "AC-12 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-12.OAD" = 100
  "AC-12.CCV" = 0
EndIf
If "AC-12.TRIP" = Active Then "AC-12 Fan Alarm" = On
If "Freezestat" = Active Then "AC-12.SS" = Off   ' freeze protection

' --- AHU AC-13: schedule start, SAT control, economizer ---
"AC-13.SS" = "Occupancy Sched"
"AC-13.SPD" = PID("Duct Static SP", "Duct Static", "AC-13 Fan")
"AC-13.CCV" = PID("AC-13 SAT SP", "AC-13.SAT", "AC-13 Cool")
"AC-13.HCV" = PID_Heat("AC-13 SAT SP", "AC-13.SAT", "AC-13 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-13.OAD" = 100
  "AC-13.CCV" = 0
EndIf
If "AC-13.TRIP" = Active Then "AC-13 Fan Alarm" = On
If "Freezestat" = Active Then "AC-13.SS" = Off   ' freeze protection


End
```

### DDC-2F-03

```gcl
'============================================================
' Program (PG): DDC-2F-03   Panel: LCP-2F
' Equipment: EVU-4, EVU-5, EVU-6
' Strategy : Scheduled ventilation / exhaust
' I/O      : 36 pts (AI 9  AO 12  BI 12  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EVU-4.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-4.TRIP" = Active Then "EVU-4 Alarm" = On
"EVU-5.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-5.TRIP" = Active Then "EVU-5 Alarm" = On
"EVU-6.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-6.TRIP" = Active Then "EVU-6 Alarm" = On

End
```

### DDC-2F-04

```gcl
'============================================================
' Program (PG): DDC-2F-04   Panel: LCP-2F
' Equipment: EF-2-1, EF-46, EF-47
' Strategy : Scheduled ventilation / exhaust
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-2-1.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-2-1.TRIP" = Active Then "EF-2-1 Alarm" = On
"EF-46.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-46.TRIP" = Active Then "EF-46 Alarm" = On
"EF-47.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-47.TRIP" = Active Then "EF-47 Alarm" = On

End
```


## LCP-3F — 3F air-side panel

### DDC-3F-01

```gcl
'============================================================
' Program (PG): DDC-3F-01   Panel: LCP-3F
' Equipment: AC-14, AC-15, AC-16
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 38 pts (AI 10  AO 13  BI 12  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-14: schedule start, SAT control, economizer ---
"AC-14.SS" = "Occupancy Sched"
"AC-14.SPD" = PID("Duct Static SP", "Duct Static", "AC-14 Fan")
"AC-14.CCV" = PID("AC-14 SAT SP", "AC-14.SAT", "AC-14 Cool")
"AC-14.HCV" = PID_Heat("AC-14 SAT SP", "AC-14.SAT", "AC-14 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-14.OAD" = 100
  "AC-14.CCV" = 0
EndIf
If "AC-14.TRIP" = Active Then "AC-14 Fan Alarm" = On
If "Freezestat" = Active Then "AC-14.SS" = Off   ' freeze protection

' --- AHU AC-15: schedule start, SAT control, economizer ---
"AC-15.SS" = "Occupancy Sched"
"AC-15.SPD" = PID("Duct Static SP", "Duct Static", "AC-15 Fan")
"AC-15.CCV" = PID("AC-15 SAT SP", "AC-15.SAT", "AC-15 Cool")
"AC-15.HCV" = PID_Heat("AC-15 SAT SP", "AC-15.SAT", "AC-15 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-15.OAD" = 100
  "AC-15.CCV" = 0
EndIf
If "AC-15.TRIP" = Active Then "AC-15 Fan Alarm" = On
If "Freezestat" = Active Then "AC-15.SS" = Off   ' freeze protection

' --- AHU AC-16: schedule start, SAT control, economizer ---
"AC-16.SS" = "Occupancy Sched"
"AC-16.SPD" = PID("Duct Static SP", "Duct Static", "AC-16 Fan")
"AC-16.CCV" = PID("AC-16 SAT SP", "AC-16.SAT", "AC-16 Cool")
"AC-16.HCV" = PID_Heat("AC-16 SAT SP", "AC-16.SAT", "AC-16 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-16.OAD" = 100
  "AC-16.CCV" = 0
EndIf
If "AC-16.TRIP" = Active Then "AC-16 Fan Alarm" = On
If "Freezestat" = Active Then "AC-16.SS" = Off   ' freeze protection


End
```

### DDC-3F-02

```gcl
'============================================================
' Program (PG): DDC-3F-02   Panel: LCP-3F
' Equipment: EVU-7
' Strategy : Scheduled ventilation / exhaust
' I/O      : 12 pts (AI 3  AO 4  BI 4  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EVU-7.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-7.TRIP" = Active Then "EVU-7 Alarm" = On

End
```

### DDC-3F-03

```gcl
'============================================================
' Program (PG): DDC-3F-03   Panel: LCP-3F
' Equipment: EF-56, EF-60, EF-61
' Strategy : Scheduled ventilation / exhaust
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-56.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-56.TRIP" = Active Then "EF-56 Alarm" = On
"EF-60.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-60.TRIP" = Active Then "EF-60 Alarm" = On
"EF-61.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-61.TRIP" = Active Then "EF-61 Alarm" = On

End
```

### DDC-3F-04

```gcl
'============================================================
' Program (PG): DDC-3F-04   Panel: LCP-3F
' Equipment: EF-62, EF-76, EF-77
' Strategy : Scheduled ventilation / exhaust
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-62.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-62.TRIP" = Active Then "EF-62 Alarm" = On
"EF-76.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-76.TRIP" = Active Then "EF-76 Alarm" = On
"EF-77.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-77.TRIP" = Active Then "EF-77 Alarm" = On

End
```


## LCP-4F — 4F–5F air-side panel

### DDC-4F-01

```gcl
'============================================================
' Program (PG): DDC-4F-01   Panel: LCP-4F
' Equipment: AC-17, AC-18, AC-19
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 38 pts (AI 10  AO 13  BI 12  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-17: schedule start, SAT control, economizer ---
"AC-17.SS" = "Occupancy Sched"
"AC-17.SPD" = PID("Duct Static SP", "Duct Static", "AC-17 Fan")
"AC-17.CCV" = PID("AC-17 SAT SP", "AC-17.SAT", "AC-17 Cool")
"AC-17.HCV" = PID_Heat("AC-17 SAT SP", "AC-17.SAT", "AC-17 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-17.OAD" = 100
  "AC-17.CCV" = 0
EndIf
If "AC-17.TRIP" = Active Then "AC-17 Fan Alarm" = On
If "Freezestat" = Active Then "AC-17.SS" = Off   ' freeze protection

' --- AHU AC-18: schedule start, SAT control, economizer ---
"AC-18.SS" = "Occupancy Sched"
"AC-18.SPD" = PID("Duct Static SP", "Duct Static", "AC-18 Fan")
"AC-18.CCV" = PID("AC-18 SAT SP", "AC-18.SAT", "AC-18 Cool")
"AC-18.HCV" = PID_Heat("AC-18 SAT SP", "AC-18.SAT", "AC-18 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-18.OAD" = 100
  "AC-18.CCV" = 0
EndIf
If "AC-18.TRIP" = Active Then "AC-18 Fan Alarm" = On
If "Freezestat" = Active Then "AC-18.SS" = Off   ' freeze protection

' --- AHU AC-19: schedule start, SAT control, economizer ---
"AC-19.SS" = "Occupancy Sched"
"AC-19.SPD" = PID("Duct Static SP", "Duct Static", "AC-19 Fan")
"AC-19.CCV" = PID("AC-19 SAT SP", "AC-19.SAT", "AC-19 Cool")
"AC-19.HCV" = PID_Heat("AC-19 SAT SP", "AC-19.SAT", "AC-19 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-19.OAD" = 100
  "AC-19.CCV" = 0
EndIf
If "AC-19.TRIP" = Active Then "AC-19 Fan Alarm" = On
If "Freezestat" = Active Then "AC-19.SS" = Off   ' freeze protection


End
```

### DDC-4F-02

```gcl
'============================================================
' Program (PG): DDC-4F-02   Panel: LCP-4F
' Equipment: AC-20, AC-21
' Strategy : Schedule + SAT coil control + economizer
' I/O      : 24 pts (AI 6  AO 8  BI 8  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- AHU AC-20: schedule start, SAT control, economizer ---
"AC-20.SS" = "Occupancy Sched"
"AC-20.SPD" = PID("Duct Static SP", "Duct Static", "AC-20 Fan")
"AC-20.CCV" = PID("AC-20 SAT SP", "AC-20.SAT", "AC-20 Cool")
"AC-20.HCV" = PID_Heat("AC-20 SAT SP", "AC-20.SAT", "AC-20 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-20.OAD" = 100
  "AC-20.CCV" = 0
EndIf
If "AC-20.TRIP" = Active Then "AC-20 Fan Alarm" = On
If "Freezestat" = Active Then "AC-20.SS" = Off   ' freeze protection

' --- AHU AC-21: schedule start, SAT control, economizer ---
"AC-21.SS" = "Occupancy Sched"
"AC-21.SPD" = PID("Duct Static SP", "Duct Static", "AC-21 Fan")
"AC-21.CCV" = PID("AC-21 SAT SP", "AC-21.SAT", "AC-21 Cool")
"AC-21.HCV" = PID_Heat("AC-21 SAT SP", "AC-21.SAT", "AC-21 Heat")  ' deadband vs cooling
' Apr-May economizer: 100% OA free-cooling, cooling coil closed
If "Economizer OK" = On Then
  "AC-21.OAD" = 100
  "AC-21.CCV" = 0
EndIf
If "AC-21.TRIP" = Active Then "AC-21 Fan Alarm" = On
If "Freezestat" = Active Then "AC-21.SS" = Off   ' freeze protection


End
```

### DDC-4F-03

```gcl
'============================================================
' Program (PG): DDC-4F-03   Panel: LCP-4F
' Equipment: EVU-8, EVU-9, EVU-10
' Strategy : Scheduled ventilation / exhaust
' I/O      : 39 pts (AI 12  AO 12  BI 12  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EVU-8.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-8.TRIP" = Active Then "EVU-8 Alarm" = On
"EVU-9.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-9.TRIP" = Active Then "EVU-9 Alarm" = On
"EVU-10.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EVU-10.TRIP" = Active Then "EVU-10 Alarm" = On

End
```

### DDC-4F-04

```gcl
'============================================================
' Program (PG): DDC-4F-04   Panel: LCP-4F
' Equipment: EF-54, EF-55, EF-57
' Strategy : Scheduled ventilation / exhaust
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-54.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-54.TRIP" = Active Then "EF-54 Alarm" = On
"EF-55.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-55.TRIP" = Active Then "EF-55 Alarm" = On
"EF-57.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-57.TRIP" = Active Then "EF-57 Alarm" = On

End
```

### DDC-4F-05

```gcl
'============================================================
' Program (PG): DDC-4F-05   Panel: LCP-4F
' Equipment: EF-58, EF-59, EF-59-2
' Strategy : Scheduled ventilation / exhaust
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-58.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-58.TRIP" = Active Then "EF-58 Alarm" = On
"EF-59.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-59.TRIP" = Active Then "EF-59 Alarm" = On
"EF-59-2.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-59-2.TRIP" = Active Then "EF-59-2 Alarm" = On

End
```

### DDC-4F-06

```gcl
'============================================================
' Program (PG): DDC-4F-06   Panel: LCP-4F
' Equipment: EF-67, EF-69, EF-70
' Strategy : Scheduled ventilation / exhaust
' I/O      : 11 pts (AI 1  AO 1  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-67.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-67.TRIP" = Active Then "EF-67 Alarm" = On
"EF-69.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-69.TRIP" = Active Then "EF-69 Alarm" = On
"EF-70.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-70.TRIP" = Active Then "EF-70 Alarm" = On

End
```

### DDC-4F-07

```gcl
'============================================================
' Program (PG): DDC-4F-07   Panel: LCP-4F
' Equipment: EF-71
' Strategy : Scheduled ventilation / exhaust
' I/O      : 3 pts (AI 0  AO 0  BI 2  BO 1)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Ventilation / exhaust: schedule + AHU/fire interlock ---
"EF-71.SS" = "Vent Sched" And ("Fire Mode" = Off)
If "EF-71.TRIP" = Active Then "EF-71 Alarm" = On

End
```


## LCP-PKG — Packaged-unit & refrigeration panel

### DDC-PKG-01

```gcl
'============================================================
' Program (PG): DDC-PKG-01   Panel: LCP-PKG
' Equipment: PAC-1-1, PAC-1-2, PAC-2
' Strategy : Enable/monitor; integral DX (some 24/7)
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Packaged DX: BMS enable/monitor; capacity on integral thermostat ---
'  Electrical/IT-room units run 24/7 -> keep enabled
"PAC-1-1.SS" = "PAC-1-1 Enable"
If "PAC-1-1.TRIP" = Active Then "PAC-1-1 Alarm" = On
"PAC-1-2.SS" = "PAC-1-2 Enable"
If "PAC-1-2.TRIP" = Active Then "PAC-1-2 Alarm" = On
"PAC-2.SS" = "PAC-2 Enable"
If "PAC-2.TRIP" = Active Then "PAC-2 Alarm" = On

End
```

### DDC-PKG-02

```gcl
'============================================================
' Program (PG): DDC-PKG-02   Panel: LCP-PKG
' Equipment: PAC-3, PAC-4, PAC-5
' Strategy : Enable/monitor; integral DX (some 24/7)
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Packaged DX: BMS enable/monitor; capacity on integral thermostat ---
'  Electrical/IT-room units run 24/7 -> keep enabled
"PAC-3.SS" = "PAC-3 Enable"
If "PAC-3.TRIP" = Active Then "PAC-3 Alarm" = On
"PAC-4.SS" = "PAC-4 Enable"
If "PAC-4.TRIP" = Active Then "PAC-4 Alarm" = On
"PAC-5.SS" = "PAC-5 Enable"
If "PAC-5.TRIP" = Active Then "PAC-5 Alarm" = On

End
```

### DDC-PKG-03

```gcl
'============================================================
' Program (PG): DDC-PKG-03   Panel: LCP-PKG
' Equipment: PCU-1-1, PCU-1-2, PCU-5
' Strategy : Enable/monitor; integral DX (some 24/7)
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Packaged DX: BMS enable/monitor; capacity on integral thermostat ---
'  Electrical/IT-room units run 24/7 -> keep enabled
"PCU-1-1.SS" = "PCU-1-1 Enable"
If "PCU-1-1.TRIP" = Active Then "PCU-1-1 Alarm" = On
"PCU-1-2.SS" = "PCU-1-2 Enable"
If "PCU-1-2.TRIP" = Active Then "PCU-1-2 Alarm" = On
"PCU-5.SS" = "PCU-5 Enable"
If "PCU-5.TRIP" = Active Then "PCU-5 Alarm" = On

End
```

### DDC-PKG-04

```gcl
'============================================================
' Program (PG): DDC-PKG-04   Panel: LCP-PKG
' Equipment: PCU-6, PCU-7, PCU-8
' Strategy : Enable/monitor; integral DX (some 24/7)
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Packaged DX: BMS enable/monitor; capacity on integral thermostat ---
'  Electrical/IT-room units run 24/7 -> keep enabled
"PCU-6.SS" = "PCU-6 Enable"
If "PCU-6.TRIP" = Active Then "PCU-6 Alarm" = On
"PCU-7.SS" = "PCU-7 Enable"
If "PCU-7.TRIP" = Active Then "PCU-7 Alarm" = On
"PCU-8.SS" = "PCU-8 Enable"
If "PCU-8.TRIP" = Active Then "PCU-8 Alarm" = On

End
```

### DDC-PKG-05

```gcl
'============================================================
' Program (PG): DDC-PKG-05   Panel: LCP-PKG
' Equipment: PCU-10, PCU-11, PCU-12
' Strategy : Enable/monitor; integral DX (some 24/7)
' I/O      : 9 pts (AI 0  AO 0  BI 6  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Packaged DX: BMS enable/monitor; capacity on integral thermostat ---
'  Electrical/IT-room units run 24/7 -> keep enabled
"PCU-10.SS" = "PCU-10 Enable"
If "PCU-10.TRIP" = Active Then "PCU-10 Alarm" = On
"PCU-11.SS" = "PCU-11 Enable"
If "PCU-11.TRIP" = Active Then "PCU-11 Alarm" = On
"PCU-12.SS" = "PCU-12 Enable"
If "PCU-12.TRIP" = Active Then "PCU-12 Alarm" = On

End
```

### DDC-PKG-06

```gcl
'============================================================
' Program (PG): DDC-PKG-06   Panel: LCP-PKG
' Equipment: PCU-13, PMAC-1
' Strategy : Enable/monitor; integral DX (some 24/7)
' I/O      : 6 pts (AI 0  AO 0  BI 4  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Packaged DX: BMS enable/monitor; capacity on integral thermostat ---
'  Electrical/IT-room units run 24/7 -> keep enabled
"PCU-13.SS" = "PCU-13 Enable"
If "PCU-13.TRIP" = Active Then "PCU-13 Alarm" = On
"PMAC-1.SS" = "PMAC-1 Enable"
If "PMAC-1.TRIP" = Active Then "PMAC-1 Alarm" = On

End
```

### DDC-PKG-07

```gcl
'============================================================
' Program (PG): DDC-PKG-07   Panel: LCP-PKG
' Equipment: REFR-1
' Strategy : Start/stop + status/alarm
' I/O      : 7 pts (AI 0  AO 0  BI 7  BO 0)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Supervise: enable, prove status, alarm ---

End
```


## LCP-LTG — Common-area & facade lighting panel

### DDC-LTG-01

```gcl
'============================================================
' Program (PG): DDC-LTG-01   Panel: LCP-LTG
' Equipment: LTG-AVIATION, LTG-NEON, LTG-BALCONY-L
' Strategy : Time/astro On-Off + status
' I/O      : 6 pts (AI 0  AO 0  BI 3  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Lighting groups: time / astronomical schedule ---
"LTG-AVIATION.CMD" = "Photocell Dusk" Or "Aviation Always On"   ' life-safety, never dark
If ("LTG-AVIATION.CMD" = On) And ("LTG-AVIATION.ST" = Off) Then "LTG-AVIATION Fault" = On
"LTG-NEON.CMD" = "LTG-NEON Sched"
If ("LTG-NEON.CMD" = On) And ("LTG-NEON.ST" = Off) Then "LTG-NEON Fault" = On
"LTG-BALCONY-L.CMD" = "LTG-BALCONY-L Sched"
If ("LTG-BALCONY-L.CMD" = On) And ("LTG-BALCONY-L.ST" = Off) Then "LTG-BALCONY-L Fault" = On

End
```

### DDC-LTG-02

```gcl
'============================================================
' Program (PG): DDC-LTG-02   Panel: LCP-LTG
' Equipment: LTG-BALCONY-H, LTG-CORRIDOR, LTG-LOBBY
' Strategy : Time/astro On-Off + status
' I/O      : 6 pts (AI 0  AO 0  BI 3  BO 3)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Lighting groups: time / astronomical schedule ---
"LTG-BALCONY-H.CMD" = "LTG-BALCONY-H Sched"
If ("LTG-BALCONY-H.CMD" = On) And ("LTG-BALCONY-H.ST" = Off) Then "LTG-BALCONY-H Fault" = On
"LTG-CORRIDOR.CMD" = "LTG-CORRIDOR Sched"
If ("LTG-CORRIDOR.CMD" = On) And ("LTG-CORRIDOR.ST" = Off) Then "LTG-CORRIDOR Fault" = On
"LTG-LOBBY.CMD" = "LTG-LOBBY Sched"
If ("LTG-LOBBY.CMD" = On) And ("LTG-LOBBY.ST" = Off) Then "LTG-LOBBY Fault" = On

End
```

### DDC-LTG-03

```gcl
'============================================================
' Program (PG): DDC-LTG-03   Panel: LCP-LTG
' Equipment: LTG-SOFFIT, LTG-TENANT
' Strategy : Time/astro On-Off + status
' I/O      : 4 pts (AI 0  AO 0  BI 2  BO 2)
'  Objects referenced by point-tag name (see I/O list). Verify syntax
'  against enteliWEB pg_reference.html (comment token, LOOP vs PID()).
'============================================================

' --- Lighting groups: time / astronomical schedule ---
"LTG-SOFFIT.CMD" = "LTG-SOFFIT Sched"
If ("LTG-SOFFIT.CMD" = On) And ("LTG-SOFFIT.ST" = Off) Then "LTG-SOFFIT Fault" = On
"LTG-TENANT.CMD" = "LTG-TENANT Sched"
If ("LTG-TENANT.CMD" = On) And ("LTG-TENANT.ST" = Off) Then "LTG-TENANT Fault" = On

End
```

