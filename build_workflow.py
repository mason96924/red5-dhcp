"""build_workflow.py -- one-project execution workflow.

The 2026-09-05 plan split the same work into four contracts. This rebuild keeps
that work, and the same nine-month elapsed duration, under a single contract.
The completion date is the contract date plus nine months. The work is five
overlapping phases of one continuous delivery — P1 fabrication, P2 device
network, P3 installation, P4 instruments, P5 programming — not four segments.

  exports/red5-dhcp_workflow-plan.{csv,xlsx,html}
  exports/red5-dhcp_workflow-gantt.svg
  docs/workflow_plan.md

What this version pins down:

1. ONE CONTRACT, SAME DURATION. Fabrication, cabling, installation,
   instrumentation and programming are overlapping phases of one delivery. Nothing is
   added to the nine months. The contract date is the only date that moves
   the completion date.

2. DEVICE NETWORK. The 2002 trunk drawing says IPEV-S 0.9 mm². The installed
   Azbil network may instead be IEIEJ p-A. That cable is not assumed reusable.
   New device-network cabling is surveyed, designed and pulled inside the
   existing window, and each segment is proved before its cutover wave.

3. THE PER-PANEL CYCLE. One crew still touches each panel inside one overnight
   window, 67 times. The handovers inside that night are stage gates of one
   contract, timed to the hour. See PANEL_CYCLE.

4. HOLD POINTS. Gates are witnessed inside the one contract. HOLDS is derived
   from the step tables.

Quantities come from panels_schedule.json. Step durations are the same planning
estimates as the 2026-09-05 workflow.
"""
from __future__ import annotations

import csv
import datetime
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(HERE, "exports")
DOCS_DIR = os.path.join(HERE, "docs")
SCHEDULE = os.path.join(HERE, "panels_schedule.json")
TODAY = datetime.date.today().isoformat()

_sched = json.load(open(SCHEDULE, encoding="utf-8"))
SRC = _sched.get("source", "")
N_PANELS = len(_sched["panels"])
N_POINTS = _sched["usedTotal"]
N_CAP = _sched["capTotal"]
N_MODULES = sum(_sched["modTotals"])
T = _sched["typeTotals"]
N_AI, N_AO, N_BTOT = T["AI"], T["AO"], T["BTOT"]
N_ANALOG = N_AI + N_AO
N_BINARY = T["DI"] + T["DO"]
N_DDC = 109
N_FUNC_POINTS = 1383
N_DEVICES = 259

TITLE = "Red5-DHCP — workflow plan, one project"
SUBTITLE = (
    f"Continuous delivery of the same {N_PANELS} panels and {N_POINTS:,} points under one contract. "
    f"Five phases overlap across nine months: P1 fabrication, P2 device network, P3 installation, "
    f"P4 instruments, P5 programming. The completion date is the contract date plus nine months. "
    f"DEJ is the prime contractor. TYBMS is subcontracted to DEJ. Furukawa Denki is not a party."
)

# Internal keys stay S1 / N / S2 / S3 / S4. The plan the reader sees uses phases.
_PHASE = {"S1": "P1", "N": "P2", "S2": "P3", "S3": "P4", "S4": "P5"}
_PHASE_WORD = {
    "S1": "Phase 1", "N": "Phase 2", "S2": "Phase 3", "S3": "Phase 4", "S4": "Phase 5",
}


def phrase(value):
    """Show phase codes. Leave cable-run uses of the word segment untouched."""
    if not isinstance(value, str):
        return value
    return re.sub(r"\b(S1|S2|S3|S4|N)\b", lambda m: _PHASE[m.group(1)], value)


def phase_heading(code, title):
    return f"{_PHASE_WORD[code]} — {title}"

# --- who does what ---------------------------------------------------------
OWNERS = [
    ("DEJ", "Prime contractor — submits the proposal and holds the main contract"),
    ("TYBMS", "BMS subcontractor to DEJ — design, programming, installation supervision, commissioning"),
    ("HOTEL", "ANA InterContinental Tokyo operations — plant availability, guest impact, area acceptance"),
    ("FAB", "Panel builder / factory — enclosure manufacture, bench load, FAT"),
    ("DHC", "District heating & cooling operator — intake coordination"),
    ("FA", "Fire-alarm contractor — life-safety interlock coordination"),
]

# --- segment meta ----------------------------------------------------------
# code -> (title, nature, window, entry[], exit[])
SEG_META = {
    "S1": (
        "Panel fabrication, supply & factory acceptance",
        "Off-site manufacture / supply",
        "C+0 to C+6 mo — same six-month off-site window",
        [
            "The single contract is executed, and the licence position for off-site manufacture versus site work is recorded in writing",
            "Panel schedule and I/O list frozen as the contract baseline",
            "As-built Azbil termination drawings available for the old→new cross-reference",
        ],
        [
            f"{N_PANELS} panels delivered to site against signed delivery notes",
            "FAT certificate held for every panel; none shipped on a failed FAT",
            "As-built panel drawings and terminal schedules issued to S2",
            "Head-end hardware staged; spares schedule issued",
        ],
    ),
    "S2": (
        "Panel replacement & field termination",
        "Electrical installation (on-site construction)",
        "C+5 mo mobilise · C+6 to C+8 mo by wave",
        [
            "S1 panels delivered and FAT'd for that wave",
            "Method statement and night-work window approved by the hotel",
            "Foreign-personnel scope, insurance liability and safety responsibility confirmed in writing",
            "Manual-operation arrangement accepted by hotel operations for the plant affected",
        ],
        [
            f'"Wired" and "Terminated" signed for all {N_POINTS:,} points',
            "Continuity and insulation records within limits for every panel",
            "Every new device-network segment proved before its wave; IEIEJ p-A not reused",
            "Rollback arrangement demonstrated and then withdrawn per wave",
        ],
    ),
    "S3": (
        "Field instrumentation replacement & calibration",
        "Instrumentation installation (on-site construction)",
        "C+6 to C+8 mo, following panel replacement inside each wave",
        [
            "Panel energised and analog cores landed by S2 for that area",
            "Reference instruments carrying in-date traceable calibration certificates",
            "Hydronic and air-side isolations agreed against the manual-operation state",
        ],
        [
            f'"P2P verified" signed for all {N_ANALOG} analog points',
            f"Two-point calibration recorded for every AI ({N_AI}); stroke test for every AO ({N_AO})",
            f"{N_BTOT} pulse interfaces proven for count and scaling",
            "Loop schedules issued marked with as-installed range, units and calibration date",
        ],
    ),
    "S4": (
        "Programming, integration, tuning & handover",
        "Engineering / software services",
        "C+1 mo authoring · C+5 mo head-end · C+6 mo through completion",
        [
            "Programming starts in month C+1 under the same contract — the factory cannot bench-load without the programs",
            "Sequence of operations baselined (docs/control_logic.md, R-1 narrative)",
            "Panel released by S2 and its analog loops verified by S3, per panel",
        ],
        [
            f'"Func. test" signed for all {N_POINTS:,} points',
            f"{N_DDC} programs loaded and version-controlled",
            "Every controller demonstrated against its SOO; 24–48 h stable trend before auto",
            "R-1 optimiser commissioned, seasonal tuning complete, operator sign-off obtained",
        ],
    ),
}

WF_COLS = ["Step", "Stage", "Activity", "Detail", "Owner", "Duration",
           "Output / evidence", "Hold point"]

# --- S1 --------------------------------------------------------------------
WF_S1 = [
    ("S1.1", "Award", "Contract award & kickoff",
     "DEJ submits the proposal and holds the main contract with the client. TYBMS is subcontracted to DEJ "
     "for the BMS scope. Furukawa Denki is not a party. Appoint a PM at DEJ and at TYBMS, and record the "
     "licence position in writing. Off-site manufacture can proceed while any construction-licence question "
     "for the site work is still open.",
     "DEJ / TYBMS", "2 wk", "Signed contract, subcontract, PM appointments, licence position memo",
     "Licence position confirmed in writing"),
    ("S1.2", "Design", "Panel schedule & point-list freeze",
     f"Sign off {N_PANELS} panels / {N_MODULES} controllers and modules / {N_CAP:,}-point capacity and the "
     f"{N_POINTS:,}-point I/O list as the frozen baseline. Everything downstream is quantified against this, "
     "so any later change is a priced variation rather than a silent scope creep.",
     "TYBMS, accepted by DEJ", "2 wk", "Frozen panel schedule and I/O list, rev A",
     "Baseline frozen before any PO"),
    ("S1.3", "Design", "Panel GA, wiring & termination drawings",
     "Produce general-arrangement, internal wiring and terminal schedules per panel, including the old Azbil "
     "terminal → new DDC terminal cross-reference. That cross-reference is what turns S2's night work into a "
     "core-for-core transfer instead of an interpretation exercise.",
     "TYBMS", "3 wk", "GA + termination drawings, old→new cross-reference",
     "Drawing approval by DEJ"),
    ("S1.4", "Interface", "Receive GCL+ bench package from S4",
     "Take the program set from Phase 5 so panels can ship pre-loaded. Authoring starts in "
     "month C+1 under the same contract. There is no second award to wait for.",
     "S4 → TYBMS", "interface", "Program package issued for bench load", "—"),
    ("S1.5", "Procure", "PO release — long-lead controllers",
     "Release the Delta controller and I/O module orders about one month after the contract date. At 12–16 "
     "weeks this lead still sets the site window. A later purchase order does not lengthen the nine months; "
     "it pushes the cutover out of the shoulder season if the contract date was early October.",
     "TYBMS, under DEJ", "12–16 wk lead", "PO acknowledgements, delivery schedule",
     "PO about one month after the contract date"),
    ("S1.6", "Build", "Enclosure fabrication & internal wiring",
     "Build and wire the enclosures in cutover-wave order — Wave 0 central and Wave 1 penthouse first — so "
     "delivery sequence matches the site sequence and nothing sits in storage for months.",
     "FAB", "8 wk rolling", "Panels built, internal wiring complete", "—"),
    ("S1.7", "Build", "Bench load & simulated I/O",
     "Load each panel's GCL+ program, address the modules, and simulate every I/O channel on the bench. Faults "
     "found here cost minutes; the same fault found at 03:00 on site costs the night.",
     "FAB + TYBMS", "1 d / panel", "Bench test record per panel", "—"),
    ("S1.8", "Test", "Factory acceptance test, witnessed",
     "Witnessed FAT per panel: module count against the schedule, addressing, power-up, simulated I/O and "
     "program verification.",
     "TYBMS, witnessed by DEJ", "1 d / batch", "FAT certificate per panel",
     "No panel ships on a failed FAT"),
    ("S1.9", "Build", "Head-end hardware staging",
     "Assemble, image and stage the servers replacing the BMS / SMS / DSS roles plus the two operator console "
     "positions, ready for S4 to stand up in parallel with the FX2 central.",
     "TYBMS", "3 wk", "Head-end staged and imaged", "—"),
    ("S1.10", "Ship", "Labelling, packing & spares",
     "Label every panel per the panel schedule, pack for the actual site access route and lift constraints, and "
     "issue the spares schedule with a recommended holding.",
     "FAB", "2 wk", "Packing list, spares schedule", "—"),
    ("S1.11", "Deliver", "Delivery to site by wave",
     "Deliver in wave order to agreed lay-down areas. The signed delivery note transfers the panels. No site "
     "work is involved in the delivery itself.",
     "FAB → DEJ", "rolling", "Signed delivery notes", "Delivery acceptance per wave"),
    ("S1.12", "Close", "As-built panel documentation",
     "Issue as-built panel drawings and terminal schedules reflecting what was actually built, since this is "
     "what S2 wires to.",
     "TYBMS", "2 wk", "As-built drawings, terminal schedules", "S1 completion certificate"),
]

# --- S2 --------------------------------------------------------------------
WF_S2 = [
    ("S2.1", "Mobilise", "Award & site mobilisation",
     "Site office and store, access routes, lift and hoist bookings, waste route, and hotel security induction "
     "for every crew member including any Korean personnel.",
     "DEJ / TYBMS", "2 wk", "Mobilisation record, induction register",
     "Foreign-personnel scope, insurance and safety responsibility confirmed in writing"),
    ("S2.2", "Plan", "Method statement & risk assessment per wave",
     "Per-area method statement and RAMS: permit regime, night-work windows, noise and dust control, guest-"
     "impact plan, and the escape and life-safety routes that must stay clear.",
     "TYBMS", "1 wk / wave", "Approved method statement + RAMS",
     "Hotel approval of method statement"),
    ("S2.3", "Survey", "Pre-cutover panel survey",
     "Per panel, verify the as-built terminations against the schedule, photograph the existing panel, and tag "
     "every core. Discrepancies are raised as variations before the night, not discovered during it.",
     "TYBMS", "0.5 d / panel", "Marked-up survey sheet, photo record", "—"),
    ("S2.4", "Prep", "Establish manual-operation arrangement",
     "Put that panel's plant into the playbook state — COS→手元, fans hand-ON, OA damper ~100 % for economizer, "
     "pumps hand-ON at fixed speed, DHC coil valves left crackable — and rehearse it with hotel operations. "
     "Only one system sits in manual at a time.",
     "TYBMS + HOTEL", "2 h / panel", "Manual arrangement sheet, ops acknowledgement",
     "Hotel ops accept the manual state before isolation"),
    ("S2.5", "Isolate", "Permit to work & isolation",
     "Lock off, prove dead, and confirm no life-safety interlock is affected — smoke control, stair "
     "pressurization and exhaust stay live and coordinated with the fire-alarm system, and the aviation "
     "obstruction light stays lit.",
     "TYBMS + HOTEL + FA", "1 h / panel", "Permit, isolation certificate",
     "Life-safety interlocks confirmed unaffected"),
    ("S2.6", "Remove", "Remove Azbil panel, retain rollback",
     "Remove the RS / RCP / CP panel but leave the old controller landed on a marshalling strip, so FX2 can be "
     "restored within minutes if the night goes wrong.",
     "TYBMS", "1–2 h / panel", "Rollback arrangement photographed", "—"),
    ("S2.7", "Install", "Install and energise the DDC panel",
     "Mount, power, earth and dress the containment; confirm supply quality and that panel labelling matches "
     "the schedule before any field core is moved.",
     "TYBMS", "2 h / panel", "Panel installed and energised", "—"),
    ("S2.8", "Terminate", "Transfer field terminations",
     f"Land the cores core-for-core against the S1 cross-reference — {N_POINTS:,} across the estate "
     f"({N_BINARY:,} binary, {N_BTOT} pulse, {N_ANALOG} analog).",
     "TYBMS", "3–5 h / panel", "Terminations complete, schedule marked as-installed", "—"),
    ("S2.9", "Network", "Land the panel on the new device network",
     "Connect the new panel to the device-network segment already proved under phase N. Do not land it on "
     "IEIEJ p-A, and do not treat the old IPEV-S trunk as reusable unless N.2 recorded that the installed "
     "cable passed the new-network test. Neighbours on the new segment must still be communicating when the "
     "crew leaves.",
     "TYBMS", "1 h / panel", "Panel on the proved new segment",
     "New segment proved before this panel is cut over"),
    ("S2.10", "Test", "Continuity & insulation testing",
     "Test and record per panel. Any core outside limits is investigated before loads are energised, not "
     "after.",
     "TYBMS", "1 h / panel", "Continuity and insulation records", "—"),
    ("S2.11", "Sign", "Sign Wired + Terminated",
     "Sign the two wiring columns of the per-panel commissioning checklist. This is the stage gate for this "
     "panel under the single contract.",
     "TYBMS, accepted by DEJ", "per panel", "Per-panel wiring completion certificate",
     "Wiring completion certificate witnessed"),
    ("S2.12", "Handover", "Release the panel to S3 and S4",
     "Release the panel the same night so instrumentation and programming happen inside the same window. DEJ "
     "names the night-shift authority, so the handover note is timed.",
     "TYBMS", "—", "Timed handover note", "—"),
    ("S2.13", "Close", "Making good & wave close-out",
     "Containment, labels, penetrations and fire-stopping, cleaning down, and clearing the snag list for the "
     "area before the wave is signed off.",
     "TYBMS", "1 wk / wave", "Wave close-out certificate", "Area wave close-out"),
]

# --- S3 --------------------------------------------------------------------
WF_S3 = [
    ("S3.1", "Mobilise", "Award & calibration setup",
     "Mobilise the instrument crew and prove the reference instruments carry in-date, traceable calibration "
     "certificates — without traceability the calibration records are not acceptance evidence.",
     "DEJ / TYBMS", "1 wk", "Reference instrument certificates",
     "Traceability evidence accepted"),
    ("S3.2", "Plan", "Loop schedule review",
     f"Reconcile {N_ANALOG} analog loops ({N_AI} AI + {N_AO} AO) and {N_BTOT} pulse interfaces against the I/O "
     "list engineering units, and flag which wells, averaging elements and impulse lines need mechanical "
     "isolation.",
     "TYBMS", "1 wk", "Loop schedule rev A with as-found ranges", "—"),
    ("S3.3", "Isolate", "Mechanical isolation per loop",
     "Isolate, drain or vent as required, coordinating every hydronic isolation with the manual-operation "
     "state so duty or standby plant always remains available.",
     "TYBMS + HOTEL", "per loop", "Isolation record",
     "Duty / standby availability confirmed"),
    ("S3.4", "Replace", f"Replace {N_AI} analog input devices",
     "Temperature, humidity, pressure, flow and energy devices, renewing immersion wells, averaging elements "
     "and impulse lines where the existing installation will not give a true reading.",
     "TYBMS", "1–2 h / loop", "Devices installed", "—"),
    ("S3.5", "Replace", f"Replace {N_AO} analog output devices",
     "Modulating valve and damper actuators. Fail-safe position and direction of action are confirmed on "
     "installation — a valve that fails the wrong way is a plant risk the sequences cannot correct.",
     "TYBMS", "2 h / loop", "Actuators installed, fail position confirmed",
     "Fail-safe position verified before auto operation"),
    ("S3.6", "Configure", "Re-range & scale each loop",
     "Configure each transmitter to the I/O list engineering units and confirm the controller-side scaling "
     "matches, so the head-end and the field agree on what the number means.",
     "TYBMS", "per loop", "Configuration record", "—"),
    ("S3.7", "Test", "Two-point calibration, every AI",
     "Calibrate each analog input at two points against the reference instrument, recording as-found and "
     "as-left values.",
     "TYBMS", "per loop", "Calibration certificate per loop", "—"),
    ("S3.8", "Test", "Stroke test, every AO",
     "Drive 0–50–100–0 %, verifying travel, position feedback and tight closure.",
     "TYBMS", "per loop", "Stroke test record", "—"),
    ("S3.9", "Test", f"Verify {N_BTOT} pulse / totalizer interfaces",
     "Prove count and scaling from the existing meters. These are verified, not replaced — the meters stay, "
     "only the interface into the new controller changes.",
     "TYBMS", "per meter", "Pulse verification record", "—"),
    ("S3.10", "Sign", "Sign P2P verified",
     "Sign the P2P column for the analog loops, with the new controller reading true value against the "
     "reference instrument. This is the instrument stage gate for this panel.",
     "TYBMS, accepted by DEJ", "per panel", "P2P signature + calibration certificates",
     "S3 acceptance per panel"),
    ("S3.11", "Close", "Issue as-installed loop schedules",
     "Issue loop schedules marked with as-installed range, units and calibration date, so the next "
     "recalibration cycle starts from fact.",
     "TYBMS", "1 wk / wave", "As-installed loop schedules", "S3 completion per wave"),
]

# --- S4 --------------------------------------------------------------------
WF_S4 = [
    ("S4.1", "Start", "Engineering kickoff in month C+1",
     "Programming starts in the contract month's successor, under the same contract as fabrication. The "
     "factory cannot bench-load a panel with a program that has not been written. This is a sequence inside "
     "the nine months, not a separate award.",
     "DEJ / TYBMS", "1 wk", "Engineering programme, point-naming convention",
     "Kickoff in month C+1"),
    ("S4.2", "Build", "Build the point database",
     f"Build the head-end database for {N_FUNC_POINTS:,} characterised points across {N_DEVICES} devices, keyed "
     "to the I/O list point tags so the graphics, programs and checklist all reference one naming scheme.",
     "TYBMS", "4 wk", "Point database rev A", "—"),
    ("S4.3", "Build", f"Author {N_DDC} GCL+ programs",
     "One PG object per controller, authored from docs/control_logic.md and the R-1 narrative, every program "
     "version-controlled. Must complete before the fabrication batches need bench loading.",
     "TYBMS", "8 wk", f"{N_DDC} programs, versioned",
     "Program review against the SOO"),
    ("S4.4", "Build", "Graphics, alarms, trends, schedules & reports",
     "Build the graphics set, alarm priorities and routing, trend logs, time programs, calendars and the "
     "periodic reporting that the operators currently get from the FX2 head-end.",
     "TYBMS", "6 wk", "Head-end configuration", "—"),
    ("S4.5", "Deploy", "Stand up the head-end in parallel with FX2",
     "Run the new head-end alongside the savic-netFX2 central and migrate the two 監視用PC consoles one at a "
     "time, so monitoring is never dark. The FX2 central is not decommissioned until the parallel run proves "
     "out.",
     "TYBMS", "3 wk", "Parallel-run record",
     "Parallel run proven before any FX2 decommissioning"),
    ("S4.6", "Interface", "Issue the bench-load package to S1",
     "Hand the program set to the factory, feeding S1.7. Late issue here pushes program loading onto the "
     "overnight site window, where there is no slack.",
     "TYBMS", "—", "Issue record", "—"),
    ("S4.7", "Deploy", "Per-panel download & comms verification",
     "Once the panel is released: download the program, verify BACnet addressing, and confirm the panel and "
     "its neighbours on the new device-network segment all communicate.",
     "TYBMS", "1 h / panel", "Comms verification record", "—"),
    ("S4.8", "Test", "Functional test, every point",
     f"Function-test every point on the panel against the I/O list — {N_POINTS:,} across the estate — and sign "
     "the Func. test column. This is the functional-test stage gate for this panel.",
     "TYBMS, accepted by DEJ", "4–8 h / panel", "Functional test sheets",
     "S4 point acceptance per panel"),
    ("S4.9", "Test", "SOO demonstration per controller",
     "Demonstrate each controller against its sequence of operations, including interlocks, staging and fail "
     "modes, witnessed by DEJ and hotel operations.",
     "TYBMS + DEJ + HOTEL", "per controller", "SOO compliance record",
     "Witnessed demonstration"),
    ("S4.10", "Prove", "24–48 h supervised trend",
     "Trend the panel for 24–48 h under supervision and review it before the plant is released to automatic "
     "control.",
     "TYBMS", "1–2 d / panel", "Trend evidence per panel",
     "Stable trend before return to auto"),
    ("S4.11", "Handover", "Return to auto & withdraw manual operation",
     "Release to automatic control, withdraw the manual-operation arrangement, and have hotel operations "
     "accept the area. Until this happens the area is still consuming the manual playbook.",
     "TYBMS + HOTEL", "per wave", "Area acceptance certificate",
     "Hotel ops area acceptance"),
    ("S4.12", "Optimise", "Commission the R-1 chiller optimiser",
     "Economic dispatch against DHC, condenser- and chilled-water reset, staging and fault detection. This "
     "needs genuine cooling load to tune against, which is why it lands in month C+8, after the waves, "
     "rather than during cutover.",
     "TYBMS", "4 wk", "Optimiser commissioning record", "—"),
    ("S4.13", "Optimise", "Seasonal tuning",
     "Tune through the first cooling season, revisiting setpoints, resets and staging against measured "
     "performance rather than design intent.",
     "TYBMS", "through season", "Tuning log with before / after evidence", "—"),
    ("S4.14", "Close", "Operator training & O&M documentation",
     "Train the operators on the new head-end and issue as-built documentation, O&M manuals and the program "
     "source set.",
     "TYBMS", "2 wk", "Training record, O&M documentation set",
     "Operator sign-off"),
    ("S4.15", "Close", "Final acceptance & defects liability start",
     "Final acceptance of the single project once every phase's evidence is complete, including the "
     "new device-network as-built. This date is the contract date plus nine months. The defects liability "
     "period starts here.",
     "DEJ / TYBMS", "—", "Final acceptance certificate", "Project completion"),
]

SEG_META["N"] = (
    "Device-network cabling",
    "New field network, inside the same contract",
    "C+0 survey · C+2 to C+6 install · proved before each wave",
    [
        "Access to sample panels, risers and the 2002 transmission-trunk drawing",
        "The new controller network cable specification is known before the survey is closed",
    ],
    [
        "Every installed run is identified as IEIEJ p-A, IPEV-S 0.9 mm², or something else",
        "IEIEJ p-A is not landed on the new panels",
        "Each wave's new segment is tested before that wave's first panel is cut over",
        "As-built cable schedule issued; abandoned cable recorded",
    ],
)

WF_N = [
    ("N.1", "Survey", "Identify the installed device-network cable",
     "Open a sample of panels and risers and record what is actually installed. The 2002 trunk drawing names "
     "IPEV-S 0.9 mm². The installed Azbil network may instead be IEIEJ p-A, or a mix of the two. Photograph "
     "the legend on the cable and the terminations. This survey runs with the drawing freeze and does not "
     "add a month.",
     "TYBMS", "2 wk", "Cable identification record, photo set",
     "Cable type recorded before the network design is approved"),
    ("N.2", "Decide", "Reuse test, or new cable",
     "IEIEJ p-A is not reused for the new controller network. A run is reused only when a test shows that "
     "the installed cable meets the new network specification. Anything that fails, including IEIEJ p-A, "
     "is designed out and left abandoned or removed. The decision is one hold point for the whole building, "
     "not a discovery on the cutover night.",
     "TYBMS, accepted by DEJ", "1 wk", "Reuse / replace decision per riser",
     "IEIEJ p-A excluded unless a test says otherwise"),
    ("N.3", "Design", "New device-network design",
     "Specify the new cable, segment lengths, shields and grounds, and the routes. Use existing containment "
     "where it has room. Follow the same floor groups as the old trunk so each cutover wave has its own "
     "segment ready. This design sits inside the same three-week drawing window as the panel GA.",
     "TYBMS", "3 wk", "Network drawings and cable schedule",
     "Network design approved with the panel drawings"),
    ("N.4", "Install", "Pull the new cable ahead of cutover",
     "Install the new risers and floor cabling during the fabrication window, while the old Azbil network "
     "is still in service. The overnight cutover then lands a panel onto a cable that is already in the "
     "building. This pull does not extend the nine months.",
     "TYBMS", "rolling, C+2 to C+6", "Installed-cable record per segment", "—"),
    ("N.5", "Test", "Prove each segment before its wave",
     "Continuity, insulation, and a communications proof on the new segment with no panel cut over yet. A "
     "wave does not start until its segment has passed.",
     "TYBMS, accepted by DEJ", "before each wave", "Segment test certificate",
     "Segment certificate signed before the wave's first panel"),
    ("N.6", "Close", "As-built network and abandoned cable",
     "Issue the as-built cable schedule. Record IEIEJ p-A and any other unused trunk as abandoned in place "
     "or removed, so a later crew does not land a new panel on it.",
     "TYBMS", "2 wk", "As-built network drawings",
     "Abandoned cable recorded before final acceptance"),
]

WORKFLOWS = [("S1", WF_S1), ("N", WF_N), ("S2", WF_S2), ("S3", WF_S3), ("S4", WF_S4)]

# --- the repeatable per-panel night cycle ----------------------------------
# One contract, one night. Repeated 67 times. The codes are stages, not awards.
CYCLE_COLS = ["Clock", "Activity", "Phase", "Owner", "Evidence / gate"]
PANEL_CYCLE = [
    ("T−14 d", "New device-network segment for this panel already proved",
     "N", "TYBMS + DEJ", "GATE — segment certificate; IEIEJ p-A not in use"),
    ("T−7 d", "Panel surveyed, spares confirmed, bench record for this panel checked",
     "S2 + S4", "TYBMS", "Survey sheet, bench test record"),
    ("T−1 d", "Method statement confirmed, hotel notified, manual arrangement rehearsed",
     "S2", "TYBMS + HOTEL", "Ops acknowledgement"),
    ("22:00", "Manual operation established on the panel's plant",
     "S2", "TYBMS + HOTEL", "GATE — manual arrangement accepted"),
    ("22:30", "Permit to work, isolate, prove dead, confirm interlocks unaffected",
     "S2", "TYBMS + HOTEL", "GATE — isolation certificate"),
    ("23:00", "Old Azbil panel removed; old controller left on the marshalling strip",
     "S2", "TYBMS", "Rollback arrangement photographed"),
    ("00:00", "New DDC panel mounted, powered, earthed, labelled",
     "S2", "TYBMS", "—"),
    ("00:30", "Field terminations transferred core-for-core",
     "S2", "TYBMS", "Marked-up termination schedule"),
    ("03:00", "Continuity and insulation tested, panel energised, Wired + Terminated signed",
     "S2", "TYBMS + DEJ", "GATE — S2 acceptance for this panel"),
    ("03:00", "Analog loops replaced, re-ranged, calibrated and P2P verified",
     "S3", "TYBMS + DEJ", "GATE — S3 acceptance for this panel"),
    ("04:00", "Program downloaded onto the new device-network segment; BACnet comms and functional test started",
     "S4", "TYBMS", "Comms verification on the proved segment, not IEIEJ p-A"),
    ("05:00", "GO / NO-GO decision",
     "all", "TYBMS + HOTEL", "GATE — NO-GO reverts to FX2 via the marshalling strip"),
    ("05:00", "Plant returned to supervised operation; 24–48 h trend started",
     "S4", "TYBMS", "Trend start record"),
    ("T+2 d", "Trend reviewed, SOO demonstrated, Func. test signed",
     "S4", "TYBMS + DEJ + HOTEL", "GATE — S4 acceptance for this panel"),
    ("T+2 d", "Panel returned to auto; manual arrangement withdrawn",
     "S2 / S4", "TYBMS + HOTEL", "GATE — area acceptance"),
]

# --- segment-to-segment interfaces ----------------------------------------
IFACE_COLS = ["From", "To", "What passes", "Evidence", "If it is missed"]
INTERFACES = [
    ("S4", "S1", "GCL+ program set for factory bench loading", "Program issue record",
     "Panels ship unloaded, so every panel needs a site download — adding an hour to a window that has none"),
    ("S1", "S2", "Panels, FAT certificates, as-built terminal schedules, old→new cross-reference",
     "Signed delivery note",
     "Crews terminate from unverified drawings, which is the classic cause of an overrun night"),
    ("S2", "S3", "Panel energised with analog cores landed", "Wired + Terminated signature",
     "The instrument crew cannot verify a loop with no live controller to read it"),
    ("N", "S2", "Proved device-network segment for the wave", "N.5 segment certificate",
     "The night has no new cable, so the crew either stops or lands the panel on IEIEJ p-A"),
    ("S2", "S4", "Panel live on the new device-network segment, neighbours still communicating",
     "N.5 certificate plus the night comms check",
     "The download fails, the panel is landed on IEIEJ p-A, or adjacent panels go dark"),
    ("S3", "S4", "Calibrated loops reading true engineering units",
     "P2P verified + calibration certificates",
     "Sequences get tuned against false values — a mistuned optimiser is worse than none"),
    ("S4", "HOTEL", "Area on automatic control with proven trend",
     "Func. test + trend evidence + area acceptance",
     "The area stays on manual, and the playbook only covers one panel at a time"),
    ("S2", "HOTEL", "Manual-operation state in force, then withdrawn", "Manual arrangement sheet",
     "Plant is left in an undefined state between two stages of the same night"),
]

# --- RACI ------------------------------------------------------------------
RACI_COLS = ["Activity", "DEJ", "TYBMS", "HOTEL", "Others"]
RACI = [
    ("Proposal and main contract", "A / R", "C", "I", "—"),
    ("Panel design & point baseline", "A", "R", "C", "—"),
    ("Device-network survey, new cable, segment proof", "A", "R", "I", "—"),
    ("Procurement & fabrication", "A", "C", "—", "R — FAB"),
    ("Factory acceptance testing", "A", "R", "I", "R — FAB"),
    ("Site installation & termination", "A", "R", "C", "—"),
    ("Manual-operation arrangement", "C", "R", "A", "—"),
    ("Life-safety interlock coordination", "A", "C", "R", "R — FA"),
    ("Instrument replacement & calibration", "A", "R", "C", "—"),
    ("DHC intake coordination", "A", "C", "R", "R — DHC"),
    ("Programming & head-end", "A", "R", "C", "—"),
    ("Functional test & SOO demonstration", "A", "R", "C", "—"),
    ("Return to auto & area acceptance", "C", "R", "A", "—"),
    ("Final acceptance & DLP", "A", "R", "C", "—"),
]

# --- schedule tensions the workflow exposes -------------------------------
TENSIONS = [
    ("DEJ is prime, TYBMS is the subcontractor", "info",
     "Furukawa Denki has backed out and does not witness. DEJ submits the proposal and holds the main "
     "contract. TYBMS is subcontracted to DEJ for the BMS work: design, programming, installation "
     "supervision and commissioning. Stage gates that Furukawa would have signed are accepted by DEJ. "
     "Hotel operations still accept the plant back to automatic control."),
    ("One contract, same nine months", "info",
     "Fabrication, cabling, installation, instrumentation and programming are overlapping phases of one "
     "continuous delivery. The elapsed duration is still nine months. The completion date is the contract "
     "date plus nine months. "
     "Moving the contract date moves the whole programme. It does not lengthen it."),
    ("Programs still have to exist before the factory loads them", "crit",
     "Bench loading still happens in months C+3 to C+5, and it still needs the application programs. Under "
     "one contract that is a sequence, not a second award: authoring starts in month C+1. If the programs "
     "are not ready, reduce the factory step to a harness test and load every program on site. That adds "
     "about an hour per panel to a night that has no spare hour."),
    ("One night-shift authority", "crit",
     "Panel replacement, instruments and the program download still meet inside one night, 67 times. They "
     "are stages of the same contract now, so there is no second contract to wait for at 03:00. DEJ names "
     "the person who makes the 05:00 GO/NO-GO. TYBMS makes the technical recommendation."),
    ("The contract date sets the season, not the duration", "warn",
     "Controller lead is still 12–16 weeks, and the purchase order still has to go out about a month after "
     "the contract date. The cutover is months C+6 and C+7. If the contract date is early October, those "
     "months are the April–May shoulder season. A later contract date keeps the nine months and lands the "
     "cutover later in the year, possibly in cooling season. The duration is not stretched to chase the "
     "shoulder season. The next comfortable slot after a missed shoulder season is about a year later, "
     "which means a later contract date, not a longer project."),
    ("IEIEJ p-A may force new device-network cabling", "crit",
     "The 2002 trunk drawing says IPEV-S 0.9 mm². The installed Azbil cable may be IEIEJ p-A. That cable "
     "is not reused unless a test shows it meets the new network specification. New cabling is surveyed in "
     "month C+0, designed with the panel drawings, and pulled during the fabrication window so each wave "
     "lands on a segment that is already proved. Finding IEIEJ p-A on the cutover night is the failure "
     "this phase exists to prevent. It does not add a month."),
    ("Rate check the durations", "info",
     "Every quantity here is derived from panels_schedule.json, but the durations are planning estimates. "
     "3–5 h to transfer a panel's terminations and 4–8 h to function-test it are the two that set the night "
     "window — have the installer confirm both against their own productivity figures before the waves are "
     "fixed."),
    ("Instrumentation may not need a full replacement", "info",
     f"The instrument phase assumes all {N_ANALOG} analog devices are replaced. If as-found calibration "
     "shows a population that is still within tolerance, that work shrinks to verification and re-ranging. "
     "Survey a sample before that scope is frozen inside the single contract."),
]

CALLOUT_HTML = {"warn": "#fdf2df", "crit": "#fbe3e3", "info": "#eef2fb", "ok": "#e7f6ec"}
SEG_HTML = {"S1": "#eef2fb", "N": "#e7f4f4", "S2": "#e7f6ec", "S3": "#fdf2df", "S4": "#f3eefb",
            "P": "#e8eef8"}
SEG_HEX = {"S1": "E7ECF5", "N": "DCEEEE", "S2": "DDF0E4", "S3": "FBEEDA", "S4": "EFE7FA",
           "P": "E4EAF6"}
SEG_STROKE = {"S1": "#4c6fae", "N": "#2a7a7a", "S2": "#3f8f5c", "S3": "#c08a2e", "S4": "#7a5ea8",
              "P": "#1F3864"}
SEG_TITLE_SHORT = {"S1": "Fabrication", "N": "Device network", "S2": "Installation",
                   "S3": "Instrumentation", "S4": "Engineering", "P": "Single contract"}


def holds():
    """Witness schedule, derived so a gate cannot exist without appearing here."""
    out = []
    for code, steps in WORKFLOWS:
        for sid, _stage, act, _detail, owner, _dur, ev, hold in steps:
            if hold and hold != "—":
                out.append((sid, code, act, hold, owner, ev))
    return out


HOLD_COLS = ["Step", "Phase", "Activity", "Hold point — work stops until signed", "Witness", "Evidence"]

# ---------------------------------------------------------------------------
# Gantt
# ---------------------------------------------------------------------------
# Nine month-slots. C+0 is the contract month. Completion sits at the end of
# C+8, which is the contract date plus nine months. If the contract date is
# 1 Oct 2026, C+0 is October 2026 and completion is the end of June 2027.
MONTHS = ["C+0", "C+1", "C+2", "C+3", "C+4", "C+5", "C+6", "C+7", "C+8"]
# (phase, label, start month index, span in months) — same spans as 2026-09-05
BARS = [
    ("N", "Survey — IEIEJ p-A or IPEV-S", 0.3, 0.7),
    ("N", "Decision and new-network design", 1.0, 1.0),
    ("N", "Pull new device-network cable", 2.2, 3.6),
    ("N", "Prove each segment before its wave", 5.2, 2.8),
    ("N", "As-built; abandoned cable recorded", 8.0, 0.8),
    ("S1", "Contract, baseline freeze & drawings", 0.0, 1.8),
    ("S1", "Procurement lead — critical path", 1.0, 3.2),
    ("S1", "Fabrication, bench load & witnessed FAT", 3.0, 2.6),
    ("S1", "Delivery to site, in wave order", 4.6, 1.4),
    ("S4", "Point database & GCL+ authoring", 1.0, 3.0),
    ("S4", "Bench-load package to factory", 3.0, 0.4),
    ("S4", "Head-end stand-up, parallel with FX2", 5.0, 1.0),
    ("S2", "Mobilise & method statements", 5.0, 0.8),
    ("S2", "Wave 0 — central head-end (parallel)", 5.2, 0.8),
    ("S2", "Wave 1 — penthouse", 6.0, 0.5),
    ("S2", "Wave 2 — guest & public floors", 6.3, 1.2),
    ("S2", "Wave 3 — basements, last", 6.9, 1.1),
    ("S3", "Mobilise, loop review & calibration setup", 5.4, 0.7),
    ("S3", "Loop replacement & calibration, by wave", 6.1, 1.7),
    ("S4", "Per-panel download, functional test & trend", 6.0, 2.1),
    ("S4", "R-1 optimiser commissioning", 8.0, 0.7),
    ("S4", "Seasonal tuning, training & handover", 8.3, 0.7),
]
# One contract rail. Award is the contract date. Acceptance is completion,
# which is the contract date plus nine months.
# (label, month index, kind) where kind = award | interim | accept
SEG_MILESTONES = [
    ("P", [
        ("Contract", 0.15, "award"),
        ("Baseline frozen", 0.8, "interim"),
        ("Cable decision", 1.15, "interim"),
        ("PO release", 1.45, "interim"),
        ("Programs to factory", 3.2, "interim"),
        ("First FAT", 3.6, "interim"),
        ("Network ready", 5.3, "interim"),
        ("Waves start", 6.05, "interim"),
        ("All areas to auto", 8.15, "interim"),
        ("Completion", 8.85, "accept"),
    ]),
]


def build_gantt():
    lab_w, m_w, row_h = 330, 88, 21
    rail_h = 46
    x0 = lab_w + 14
    top = 78
    bars_end = top + row_h * len(BARS)
    rails_top = bars_end + 44
    h = rails_top + rail_h * len(SEG_MILESTONES) + 46
    w = x0 + m_w * len(MONTHS) + 20
    p = []

    def txt(x, y, s, size=11, fill="#1b2430", weight="400", anchor="start"):
        p.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="-apple-system,Segoe UI,Roboto,'
                 f'Helvetica,Arial,sans-serif" font-size="{size}" fill="{fill}" '
                 f'font-weight="{weight}" text-anchor="{anchor}">{html.escape(s)}</text>')

    txt(14, 26, "Programme — one contract, nine months from the contract date", 14, "#1F3864", "700")
    txt(14, 44, "C+0 is the contract month. P1–P5 overlap across the same nine months. "
                "Completion is the contract date plus nine months.",
        10.5, "#5b6675")

    # month grid
    for i, m in enumerate(MONTHS):
        mx = x0 + i * m_w
        p.append(f'<rect x="{mx:.1f}" y="{top - 22:.1f}" width="{m_w}" height="20" '
                 f'fill="{"#eef1f6" if i % 2 == 0 else "#f7f9fc"}" stroke="#dde3ec"/>')
        txt(mx + m_w / 2, top - 8, m, 10.5, "#33404f", "600", "middle")
        p.append(f'<line x1="{mx:.1f}" y1="{top:.1f}" x2="{mx:.1f}" '
                 f'y2="{bars_end:.1f}" stroke="#e6eaf1"/>')
    right = x0 + m_w * len(MONTHS)
    p.append(f'<line x1="{right:.1f}" y1="{top:.1f}" x2="{right:.1f}" '
             f'y2="{bars_end:.1f}" stroke="#e6eaf1"/>')
    # Site window: months C+6 and C+7. Shoulder season only if the contract
    # date is early October. The shading does not move if the season does.
    sx = x0 + 6 * m_w
    p.append(f'<rect x="{sx:.1f}" y="{top:.1f}" width="{2 * m_w}" height="{bars_end - top}" '
             f'fill="#3f8f5c" opacity="0.055"/>')
    txt(sx + m_w, bars_end + 15, "site window — shoulder season only if the contract is early October",
        10, "#3f8f5c", "600", "middle")

    for r, (seg, label, start, span) in enumerate(BARS):
        y = top + r * row_h
        if r % 2:
            p.append(f'<rect x="14" y="{y:.1f}" width="{w - 34}" height="{row_h}" fill="#fafbfd"/>')
        txt(14, y + 14.5, f"{_PHASE[seg]}  {phrase(label)}", 11, "#1b2430")
        bx = x0 + start * m_w
        bw = max(10, span * m_w)
        fill = SEG_HTML[seg]
        p.append(f'<rect x="{bx:.1f}" y="{y + 4:.1f}" width="{bw:.1f}" height="{row_h - 8}" rx="4" '
                 f'fill="{fill}" stroke="{SEG_STROKE[seg]}" stroke-width="1.2"/>')

    # --- one milestone rail per contract -------------------------------------
    # Labels alternate above and below the rail: at 9 px a run of seven markers
    # collides on a single line, and these are contract dates, not decoration.
    def diamond(cx, cy, r, fill, stroke, sw=1.4):
        p.append(f'<polygon points="{cx:.1f},{cy - r:.1f} {cx + r:.1f},{cy:.1f} '
                 f'{cx:.1f},{cy + r:.1f} {cx - r:.1f},{cy:.1f}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}"/>')

    for si, (code, ms) in enumerate(SEG_MILESTONES):
        cy = rails_top + si * rail_h + 12
        stroke = SEG_STROKE[code]
        txt(14, cy + 4, "Project milestones — one continuous delivery", 10.5,
            "#1b2430", "600")
        xs_ = [x0 + mi * m_w for _l, mi, _k in ms]
        p.append(f'<line x1="{xs_[0]:.1f}" y1="{cy:.1f}" x2="{xs_[-1]:.1f}" y2="{cy:.1f}" '
                 f'stroke="{stroke}" stroke-width="1.5"/>')
        for i, (label, mi, kind) in enumerate(ms):
            mx = x0 + mi * m_w
            if kind == "award":
                diamond(mx, cy, 6.5, "#ffffff", stroke, 1.8)
            elif kind == "accept":
                diamond(mx, cy, 7, stroke, stroke)
            else:
                p.append(f'<circle cx="{mx:.1f}" cy="{cy:.1f}" r="3.6" fill="{stroke}"/>')
            weight = "700" if kind in ("award", "accept") else "500"
            txt(mx, cy - 11 if i % 2 == 0 else cy + 18, label, 9,
                "#1b2430" if kind in ("award", "accept") else "#5b6675", weight, "middle")

    # marker legend
    ly = rails_top + rail_h * len(SEG_MILESTONES) + 14
    lx = x0
    diamond(lx, ly, 6.5, "#ffffff", "#1F3864", 1.8)
    txt(lx + 12, ly + 3.5, "contract date", 9.5, "#33404f")
    lx += 130
    p.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3.6" fill="#1F3864"/>')
    txt(lx + 11, ly + 3.5, "interim milestone", 9.5, "#33404f")
    lx += 140
    diamond(lx, ly, 7, "#1F3864", "#1F3864")
    txt(lx + 13, ly + 3.5, "completion — the contract date plus nine months",
        9.5, "#33404f")

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="One-project nine-month programme Gantt">'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>' + "".join(p) + "</svg>")


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------
def write_csv(path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([TITLE])
        w.writerow([SUBTITLE])
        w.writerow([f"Generated {TODAY}"])
        w.writerow([])
        for code, steps in WORKFLOWS:
            title, nature, window, entry, exit_ = SEG_META[code]
            w.writerow([phase_heading(code, title)])
            w.writerow([nature, window])
            w.writerow(["Entry criteria"])
            for e in entry:
                w.writerow(["", phrase(e)])
            w.writerow(WF_COLS)
            for row in steps:
                w.writerow([phrase(c) for c in row])
            w.writerow(["Exit criteria"])
            for e in exit_:
                w.writerow(["", phrase(e)])
            w.writerow([])
        w.writerow(["Per-panel cutover cycle — repeated 67 times"])
        w.writerow(CYCLE_COLS)
        for row in PANEL_CYCLE:
            w.writerow([phrase(c) for c in row])
        w.writerow([])
        w.writerow(["Handoffs between phases"])
        w.writerow(IFACE_COLS)
        for row in INTERFACES:
            w.writerow([phrase(c) for c in row])
        w.writerow([])
        w.writerow(["Hold points / witness schedule"])
        w.writerow(HOLD_COLS)
        for row in holds():
            w.writerow([phrase(c) for c in row])
        w.writerow([])
        w.writerow(["RACI"])
        w.writerow(RACI_COLS)
        w.writerows(RACI)
        w.writerow([])
        w.writerow(["Schedule tensions"])
        w.writerow(["Item", "Severity", "Detail"])
        w.writerows(TENSIONS)


# ---------------------------------------------------------------------------
# XLSX
# ---------------------------------------------------------------------------
def write_xlsx(path):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    HDR = PatternFill("solid", fgColor="1F3864")
    HF = Font(bold=True, color="FFFFFF", size=10)
    thin = Side(style="thin", color="D9D9D9")
    B = Border(left=thin, right=thin, top=thin, bottom=thin)

    def hdr(ws, n, row=1):
        for c in range(1, n + 1):
            ws.cell(row=row, column=c).fill = HDR
            ws.cell(row=row, column=c).font = HF

    def widths(ws, ws_w):
        for i, x in enumerate(ws_w, 1):
            ws.column_dimensions[get_column_letter(i)].width = x

    def frame(ws, n, start=2):
        for rr in range(start, ws.max_row + 1):
            for c in range(1, n + 1):
                ws.cell(row=rr, column=c).border = B
                ws.cell(row=rr, column=c).alignment = Alignment(wrap_text=True, vertical="top")

    wb = Workbook()
    ws = wb.active
    ws.title = "Overview"
    ws.append([TITLE])
    ws.cell(row=1, column=1).font = Font(bold=True, size=14, color="1F3864")
    ws.append([SUBTITLE])
    ws.cell(row=2, column=1).font = Font(italic=True, size=10, color="555555")
    ws.append([f"Generated {TODAY}"])
    ws.append([])
    ws.append(["Phase", "Name", "Nature", "Window", "Steps"])
    hdr(ws, 5, row=ws.max_row)
    for code, steps in WORKFLOWS:
        title, nature, window, _e, _x = SEG_META[code]
        ws.append([_PHASE_WORD[code], title, nature, window, len(steps)])
        for c in range(1, 6):
            ws.cell(row=ws.max_row, column=c).fill = PatternFill("solid", fgColor=SEG_HEX[code])
    ws.append([])
    ws.append(["Owner", "Role"])
    hdr(ws, 2, row=ws.max_row)
    for k, v in OWNERS:
        ws.append([k, v])
    widths(ws, [14, 46, 34, 34, 80])
    for rr in range(1, ws.max_row + 1):
        for c in range(1, 6):
            ws.cell(row=rr, column=c).alignment = Alignment(wrap_text=True, vertical="top")

    for code, steps in WORKFLOWS:
        title, nature, window, entry, exit_ = SEG_META[code]
        ws = wb.create_sheet(_PHASE_WORD[code])
        ws.append([phase_heading(code, title)])
        ws.cell(row=1, column=1).font = Font(bold=True, size=13, color="1F3864")
        ws.append([f"{nature} · {window}"])
        ws.cell(row=2, column=1).font = Font(italic=True, size=10, color="555555")
        ws.append([])
        ws.append(["ENTRY CRITERIA"])
        ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
        for e in entry:
            ws.append(["", phrase(e)])
        ws.append([])
        hrow = ws.max_row + 1
        ws.append(WF_COLS)
        hdr(ws, len(WF_COLS), row=hrow)
        for row in steps:
            ws.append([phrase(c) for c in row])
            for c in range(1, len(WF_COLS) + 1):
                ws.cell(row=ws.max_row, column=c).fill = PatternFill("solid", fgColor=SEG_HEX[code])
        last = ws.max_row
        ws.append([])
        ws.append(["EXIT CRITERIA"])
        ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
        for e in exit_:
            ws.append(["", phrase(e)])
        widths(ws, [9, 13, 40, 86, 22, 16, 40, 40])
        for rr in range(hrow, last + 1):
            for c in range(1, len(WF_COLS) + 1):
                ws.cell(row=rr, column=c).border = B
                ws.cell(row=rr, column=c).alignment = Alignment(wrap_text=True, vertical="top")
        for rr in range(1, ws.max_row + 1):
            ws.cell(row=rr, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes = ws.cell(row=hrow + 1, column=1).coordinate

    ws = wb.create_sheet("Panel-cycle")
    ws.append(CYCLE_COLS)
    hdr(ws, len(CYCLE_COLS))
    for row in PANEL_CYCLE:
        ws.append([phrase(c) for c in row])
        if str(row[4]).startswith("GATE"):
            for c in range(1, len(CYCLE_COLS) + 1):
                ws.cell(row=ws.max_row, column=c).fill = PatternFill("solid", fgColor="FBEEDA")
    widths(ws, [10, 66, 12, 24, 52])
    ws.freeze_panes = "A2"
    frame(ws, len(CYCLE_COLS))

    ws = wb.create_sheet("Interfaces")
    ws.append(IFACE_COLS)
    hdr(ws, len(IFACE_COLS))
    for row in INTERFACES:
        ws.append([phrase(c) for c in row])
    widths(ws, [8, 8, 58, 40, 74])
    ws.freeze_panes = "A2"
    frame(ws, len(IFACE_COLS))

    ws = wb.create_sheet("Hold points")
    ws.append(HOLD_COLS)
    hdr(ws, len(HOLD_COLS))
    for row in holds():
        ws.append([phrase(c) for c in row])
        for c in range(1, len(HOLD_COLS) + 1):
            ws.cell(row=ws.max_row, column=c).fill = PatternFill("solid", fgColor=SEG_HEX[row[1]])
    widths(ws, [9, 7, 40, 56, 24, 40])
    ws.freeze_panes = "A2"
    frame(ws, len(HOLD_COLS))

    ws = wb.create_sheet("RACI")
    ws.append(RACI_COLS)
    hdr(ws, len(RACI_COLS))
    for row in RACI:
        ws.append(list(row))
    ws.append([])
    ws.append(["R = responsible · A = accountable · C = consulted · I = informed"])
    widths(ws, [46, 14, 14, 12, 22])
    ws.freeze_panes = "A2"
    frame(ws, len(RACI_COLS))

    ws = wb.create_sheet("Tensions")
    ws.append(["Item", "Severity", "Detail"])
    hdr(ws, 3)
    for row in TENSIONS:
        ws.append(list(row))
    widths(ws, [40, 11, 112])
    ws.freeze_panes = "A2"
    frame(ws, 3)

    wb.save(path)


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
def _wf_html():
    out = []
    for code, steps in WORKFLOWS:
        title, nature, window, entry, exit_ = SEG_META[code]
        rows = "".join(
            f'<tr{" class=hold" if hold and hold != "—" else ""}>'
            f"<td class=c><b>{html.escape(phrase(sid))}</b></td><td class=c>{html.escape(stage)}</td>"
            f"<td><b>{html.escape(phrase(act))}</b></td><td>{html.escape(phrase(detail))}</td>"
            f"<td class=c>{html.escape(phrase(owner))}</td><td class=c>{html.escape(dur)}</td>"
            f"<td>{html.escape(phrase(ev))}</td>"
            f"<td>{'<b>' + html.escape(phrase(hold)) + '</b>' if hold and hold != '—' else '—'}</td></tr>"
            for sid, stage, act, detail, owner, dur, ev, hold in steps)
        ul_in = "".join(f"<li>{html.escape(phrase(e))}</li>" for e in entry)
        ul_out = "".join(f"<li>{html.escape(phrase(e))}</li>" for e in exit_)
        out.append(
            f'<div class="seg" style="background:{SEG_HTML[code]}; border-left:6px solid {SEG_STROKE[code]}">'
            f"<h3>{html.escape(phase_heading(code, title))}</h3>"
            f'<p class="meta">{html.escape(nature)} · {html.escape(window)} · {len(steps)} steps</p>'
            f'<div class="grid2">'
            f'<div class="crit"><b>Entry criteria — do not start without these</b><ul>{ul_in}</ul></div>'
            f'<div class="crit"><b>Exit criteria — this phase is complete when</b><ul>{ul_out}</ul></div>'
            f"</div>"
            f'<table class="wf"><thead><tr>'
            + "".join(f"<th{' class=c' if c in ('Step', 'Stage', 'Owner', 'Duration') else ''}>"
                      f"{html.escape(c)}</th>" for c in WF_COLS)
            + f"</tr></thead><tbody>{rows}</tbody></table></div>")
    return "".join(out)


def _rows_html(data, center=()):
    return "".join(
        "<tr>" + "".join(
            f'<td{" class=c" if i in center else ""}>{html.escape(phrase(str(c)))}</td>'
            for i, c in enumerate(row)) + "</tr>"
        for row in data)


def _cycle_html():
    out = []
    for clock, act, seg, owner, ev in PANEL_CYCLE:
        gate = ev.startswith("GATE")
        out.append(
            f'<tr{" class=hold" if gate else ""}><td class=c><b>{html.escape(clock)}</b></td>'
            f"<td>{html.escape(phrase(act))}</td><td class=c>{html.escape(phrase(seg))}</td>"
            f"<td class=c>{html.escape(phrase(owner))}</td>"
            f"<td>{'<b>' + html.escape(phrase(ev)) + '</b>' if gate else html.escape(phrase(ev))}</td></tr>")
    return "".join(out)


def write_html(path, gantt):
    owners = "".join(f"<tr><td class=c><b>{html.escape(k)}</b></td><td>{html.escape(v)}</td></tr>"
                     for k, v in OWNERS)
    tens = "".join(
        f'<div class="call" style="background:{CALLOUT_HTML[t]}"><b>{html.escape(ti)}</b>'
        f"<p>{html.escape(tx)}</p></div>" for ti, t, tx in TENSIONS)
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<style>
  :root {{ --ink:#1b2430; --dim:#5b6675; --line:#d8dee7; --band:#1F3864; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
          color:var(--ink); background:#f4f6f9; padding:28px; }}
  .page {{ max-width:1320px; margin:0 auto; background:#fff; border:1px solid var(--line);
           border-radius:10px; padding:28px 32px; }}
  h1 {{ font-size:22px; margin:0 0 4px; }} .sub {{ color:var(--dim); margin:0 0 18px; max-width:95ch; }}
  h2 {{ font-size:16px; margin:28px 0 8px; border-bottom:2px solid var(--band);
        padding-bottom:4px; color:var(--band); }}
  h3 {{ font-size:15px; margin:0 0 2px; }}
  table {{ border-collapse:collapse; width:100%; margin:6px 0; font-size:12.5px; background:#fff; }}
  th, td {{ border:1px solid var(--line); padding:6px 8px; text-align:left; vertical-align:top; }}
  thead th {{ background:var(--band); color:#fff; font-weight:600; }}
  td.c, th.c {{ text-align:center; white-space:nowrap; }}
  tr.hold td {{ background:#fffaf0; }}
  .seg {{ border:1px solid var(--line); border-radius:8px; padding:14px 16px; margin:14px 0; }}
  .seg .meta {{ color:var(--dim); font-size:12px; margin:0 0 10px; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:10px; }}
  .crit {{ background:#fff; border:1px solid var(--line); border-radius:6px; padding:10px 12px; }}
  .crit ul {{ margin:6px 0 0; padding-left:18px; }} .crit li {{ font-size:12.5px; margin-bottom:3px; }}
  .cols {{ display:flex; gap:14px; flex-wrap:wrap; }}
  .call {{ flex:1; min-width:300px; border:1px solid var(--line); border-radius:8px; padding:12px 14px; }}
  .call b {{ display:block; margin-bottom:4px; }} .call p {{ margin:0; color:#33404f; font-size:13px; }}
  .dia {{ border:1px solid var(--line); border-radius:8px; padding:8px; margin:10px 0; overflow-x:auto; }}
  .dia svg {{ display:block; max-width:100%; height:auto; }}
  .note {{ color:var(--dim); font-size:12px; margin:4px 0 0; }}
  .foot {{ color:var(--dim); font-size:12px; margin-top:24px; }}
  @media print {{ body {{ background:#fff; padding:0; }} .page {{ border:0; }}
                  .seg, .dia {{ break-inside:avoid; }} }}
  @media (max-width:900px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
</style></head>
<body><div class="page">
<h1>{html.escape(TITLE)}</h1>
<p class="sub">{html.escape(SUBTITLE)}</p>

<h2>1 · Programme — one contract, nine months</h2>
<div class="dia">{gantt}</div>
<p class="note">C+0 is the contract month. The filled diamond is completion, the contract date plus nine
months. The bars keep the durations from the 2026-09-05 plan. Phase N is the new device network, added
because the installed Azbil cable may be IEIEJ p-A. The shaded band is the site window. It is the
April–May shoulder season only when the contract date is early October.</p>

<h2>2 · Who is who</h2>
<table><thead><tr><th class=c>Code</th><th>Role</th></tr></thead><tbody>{owners}</tbody></table>

<h2>3 · Workflow, phase by phase</h2>
<p class="note">Shaded rows are hold points: work stops there until the named witness signs. Durations are
planning estimates — the only figures here not derived from the panel schedule.</p>
{_wf_html()}

<h2>4 · The per-panel cutover cycle — repeated {N_PANELS} times</h2>
<p class="note">One contract touches the same panel inside one overnight window, {N_PANELS} times. The rows are
stages of that night, timed to the hour. The new device-network segment is already proved fourteen days
before the night. Shaded rows are gates.</p>
<table><thead><tr><th class=c>Clock</th><th>Activity</th><th class=c>Phase</th><th class=c>Owner</th>
<th>Evidence / gate</th></tr></thead><tbody>{_cycle_html()}</tbody></table>

<h2>5 · Handoffs inside the one contract</h2>
<table><thead><tr>{"".join(f'<th{" class=c" if c in ("From", "To") else ""}>{html.escape(c)}</th>' for c in IFACE_COLS)}</tr></thead>
<tbody>{_rows_html(INTERFACES, center=(0, 1))}</tbody></table>

<h2>6 · Hold points — witness schedule</h2>
<p class="note">Derived from the step tables above, so a step cannot acquire a gate without appearing here.
{len(holds())} witnessed gates across the one contract.</p>
<table><thead><tr>{"".join(f'<th{" class=c" if c in ("Step", "Phase") else ""}>{html.escape(c)}</th>' for c in HOLD_COLS)}</tr></thead>
<tbody>{_rows_html(holds(), center=(0, 1))}</tbody></table>

<h2>7 · Schedule tensions this workflow exposes</h2>
<div class="cols">{tens}</div>

<h2>8 · RACI</h2>
<table><thead><tr>{"".join(f'<th{" class=c" if i else ""}>{html.escape(c)}</th>' for i, c in enumerate(RACI_COLS))}</tr></thead>
<tbody>{_rows_html(RACI, center=(1, 2, 3, 4, 5))}</tbody></table>
<p class="note">R = responsible · A = accountable · C = consulted · I = informed</p>

<p class="foot">Generated {TODAY} · Red5-DHCP · one contract, nine months from the contract date. Quantities from
panels_schedule.json (판넬별 포인트 정리 {SRC}); sequence from build_cutover.py and build_commissioning.py.
Five overlapping phases, one continuous delivery. The 2026-09-05 four-segment draft is withdrawn. Regenerate with
<code>.venv/bin/python build_workflow.py</code>. Print to PDF for distribution. Durations are planning
estimates, not commitments.</p>
</div></body></html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------
def write_md(path):
    L = ["# Red5-DHCP — workflow plan, one project", "", SUBTITLE, "",
         f"_Generated {TODAY}. Continuous delivery in five overlapping phases. The 2026-09-05 four-segment "
         "draft is withdrawn. Quantities from `panels_schedule.json` (" + SRC + "). The nine-month duration "
         "is unchanged. The completion date is the contract date plus nine months. The phase summary is "
         "`docs/phase_plan.md`. Durations are planning estimates._", "",
         "## Who is who", ""]
    L += [f"- **{k}** — {v}" for k, v in OWNERS]

    for code, steps in WORKFLOWS:
        title, nature, window, entry, exit_ = SEG_META[code]
        L += ["", f"## {phase_heading(code, title)}", "",
              f"**Nature of work:** {nature}  ", f"**Window:** {window}  ",
              f"**Steps:** {len(steps)}", "", "### Entry criteria", ""]
        L += [f"- {phrase(e)}" for e in entry]
        L += ["", "### Workflow", "", "| " + " | ".join(WF_COLS) + " |",
              "|" + "|".join("---" for _ in WF_COLS) + "|"]
        for row in steps:
            L.append("| " + " | ".join(phrase(str(c)).replace("|", "\\|") for c in row) + " |")
        L += ["", "### Exit criteria", ""] + [f"- {phrase(e)}" for e in exit_]

    L += ["", f"## Per-panel cutover cycle — repeated {N_PANELS} times", "",
          "One contract touches the same panel inside one overnight window. The new device-network segment "
          "is proved before the night. Handovers inside the night are timed.", "",
          "| " + " | ".join(CYCLE_COLS) + " |", "|" + "|".join("---" for _ in CYCLE_COLS) + "|"]
    for row in PANEL_CYCLE:
        L.append("| " + " | ".join(phrase(str(c)) for c in row) + " |")

    L += ["", "## Handoffs between phases", "",
          "| " + " | ".join(IFACE_COLS) + " |", "|" + "|".join("---" for _ in IFACE_COLS) + "|"]
    for row in INTERFACES:
        L.append("| " + " | ".join(phrase(str(c)) for c in row) + " |")

    L += ["", f"## Hold points — witness schedule ({len(holds())} gates)", "",
          "| " + " | ".join(HOLD_COLS) + " |", "|" + "|".join("---" for _ in HOLD_COLS) + "|"]
    for row in holds():
        L.append("| " + " | ".join(phrase(str(c)) for c in row) + " |")

    L += ["", "## Schedule tensions", ""]
    for ti, sev, tx in TENSIONS:
        L += [f"### {ti} ({sev})", "", tx, ""]

    L += ["## RACI", "", "| " + " | ".join(RACI_COLS) + " |",
          "|" + "|".join("---" for _ in RACI_COLS) + "|"]
    for row in RACI:
        L.append("| " + " | ".join(str(c) for c in row) + " |")
    L += ["", "_R = responsible · A = accountable · C = consulted · I = informed_", ""]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    stem = os.path.join(EXPORT_DIR, "red5-dhcp_workflow-plan")
    gantt = build_gantt()
    with open(os.path.join(EXPORT_DIR, "red5-dhcp_workflow-gantt.svg"), "w", encoding="utf-8") as f:
        f.write(gantt)
    write_csv(stem + ".csv")
    write_xlsx(stem + ".xlsx")
    write_html(stem + ".html", gantt)
    write_md(os.path.join(DOCS_DIR, "workflow_plan.md"))

    # Every workstream needs steps, an entry gate and a witnessed hold.
    assert len(WORKFLOWS) == 5, len(WORKFLOWS)
    for code, steps in WORKFLOWS:
        assert steps, code
        assert SEG_META[code][3] and SEG_META[code][4], code
        assert any(h and h != "—" for *_x, h in steps), f"{code} has no hold point"
    # Bars and markers must not run off the end of the month grid.
    for seg, label, start, span in BARS:
        assert 0 <= start and start + span <= len(MONTHS), (seg, label, start, span)
    # One contract: a start on the contract date and one completion.
    assert [c for c, _m in SEG_MILESTONES] == ["P"]
    for code, ms in SEG_MILESTONES:
        kinds = [k for _l, _mi, k in ms]
        assert kinds[0] == "award" and kinds[-1] == "accept", (code, kinds)
        assert all(0 <= mi <= len(MONTHS) for _l, mi, _k in ms), code
        assert ms == sorted(ms, key=lambda m: m[1]), f"{code} milestones out of order"
    n_steps = sum(len(s) for _c, s in WORKFLOWS)
    print(f"workflow plan exported: {n_steps} steps across {len(WORKFLOWS)} phases, "
          f"{len(holds())} hold points, {len(PANEL_CYCLE)}-stage panel cycle "
          f"-> {stem}.{{csv,xlsx,html}} + workflow-gantt.svg + docs/workflow_plan.md")
