"""build_sld.py -- single-line architecture diagrams: existing Azbil vs proposed Delta.

Emits two SLDs plus a side-by-side comparison, for the "system architecture
diagram / network single-line diagram" package Furukawa asked for on 2026-09-03.

  exports/red5-dhcp_sld-existing.svg   Azbil savic-netFX2 as-built
  exports/red5-dhcp_sld-proposed.svg   Delta / Red5 BACnet replacement
  exports/red5-dhcp_sld.html           both + existing-vs-new comparison table

Single-line convention: one representative branch is drawn in full and its
multiplicity is annotated (x6 SCS, x4 NC-bus, x80 CON-T1L). Drawing all 67
panels would be a wiring diagram, not an SLD.

Both diagrams share the same tier skeleton and the same bottom row of field
zones, so they can be laid side by side and read as a swap. That matters for
the submission: the retrofit is a 1:1 replacement on the existing panels,
trunk routes and field wiring, and the diagram should make that obvious at a
glance rather than asserting it in prose.

Existing side is from docs/reconciliation_2026-08.md (savic-netFX2 hardware
delivery spec 1-LHP1-11 + the 2002 伝送幹線系統図 trunk drawing). Proposed side
is from the module fleet in panels_schedule.json, typed by generate_io_list.py's
Delta-Controllers sheet. Panel and point counts come from the same schedule as
build_cutover.py, so all three documents agree.
"""
from __future__ import annotations

import datetime
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(HERE, "exports")
SCHEDULE = os.path.join(HERE, "panels_schedule.json")
TODAY = datetime.date.today().isoformat()

_sched = json.load(open(SCHEDULE, encoding="utf-8"))
_PANELS = _sched["panels"]
SRC = _sched.get("source", "")
N_PANELS = len(_PANELS)
N_POINTS = _sched["usedTotal"]
N_CAP = _sched["capTotal"]
MOD = _sched["modTotals"]
N_MODULES = sum(MOD)

# panels_schedule.json module columns, typed by generate_io_list.py
N_ROOM, N_CONT, N_EXPAND, N_M4F4, N_M8, N_M8P = MOD
N_CONTROLLERS = N_ROOM + N_CONT
N_IO_MODULES = N_M4F4 + N_M8 + N_M8P

N_DDC = 109          # functional controllers -> one GCL+ program each
N_FUNC_POINTS = 1383

# Analog population = S3's whole scope, so it has to be drawn, not implied.
_TYPES = _sched["typeTotals"]
N_AI, N_AO = _TYPES["AI"], _TYPES["AO"]
N_ANALOG = N_AI + N_AO

# Field zones = the cutover waves, so the two documents cannot disagree.
ZONES = [
    ("Central head-end", "B2F 시스템 제어반", 1, 25),
    ("Penthouse PH1/PH2", "rooftop plant, R-1, OAUs", 9, 710),
    ("Guest & public floors", "31F, 21F, 10F, 4F-1F", 26, 2083),
    ("Basements B1-B3", "plant, hydronics, DHC intake", 31, 1649),
]

# ---------------------------------------------------------------------------
# SVG primitives
# ---------------------------------------------------------------------------
# CX1 is pinned rather than derived from W, so widening the canvas for the
# right-hand contract-scope column leaves every box position untouched and the
# two diagrams stay superimposable.
W = 1440
GUT = 158                      # left gutter holding the tier labels
CX0, CX1 = GUT + 12, 1176      # content band
CW = CX1 - CX0
SCOPE_X = CX1 + 20             # contract-scope column
SCOPE_W = W - 24 - SCOPE_X

INK = "#1b2430"
DIM = "#5b6675"
LINE = "#9aa6b6"
BAND = "#1F3864"

PAL = {
    "ops":    ("#eef2fb", "#c3d0ea"),
    "server": ("#e7ecf7", "#b8c6e3"),
    "net":    ("#eaf4ec", "#b9dcc2"),
    "ctrl":   ("#f3eefb", "#cfc0e8"),
    "io":     ("#fdf2df", "#e8d3a8"),
    "field":  ("#f1f4f8", "#c9d3e0"),
    "legacy": ("#fbe3e3", "#e6bcbc"),
    "new":    ("#ddf0e4", "#a9d6ba"),
}

# Phase colours, matching the workflow. Badges on the drawing use the phase
# numbers: P1 fabrication, P3 installation, P4 instruments, P5 programming.
SEGPAL = {
    "S1": ("#eef2fb", "#4c6fae"),
    "S2": ("#e7f6ec", "#3f8f5c"),
    "S3": ("#fdf2df", "#c08a2e"),
    "S4": ("#f3eefb", "#7a5ea8"),
}
SEG_NAME = {
    "S1": "Panel fabrication & supply",
    "S2": "Panel replacement & termination",
    "S3": "Instrumentation & calibration",
    "S4": "Programming & handover",
}


def esc(s):
    return html.escape(str(s), quote=True)


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.title = title
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=12, fill=INK, weight="400", anchor="start",
             family=None, opacity=None):
        fam = family or "-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif"
        op = f' opacity="{opacity}"' if opacity else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
                 f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}"{op}>{esc(s)}</text>')

    def line(self, x1, y1, x2, y2, stroke=LINE, w=1.4, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{w}"{d}/>')

    def rect(self, x, y, w, h, fill, stroke, r=6, dash=None, sw=1.2):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def box(self, x, y, w, h, title, lines=(), pal="field", dash=None, tsize=12):
        fill, stroke = PAL[pal]
        self.rect(x, y, w, h, fill, stroke, dash=dash)
        self.text(x + w / 2, y + 17, title, size=tsize, weight="700", anchor="middle")
        for i, ln in enumerate(lines):
            self.text(x + w / 2, y + 17 + 14 * (i + 1), ln, size=10.5, fill=DIM, anchor="middle")

    def chip(self, x, y, w, s, pal="net", h=22):
        fill, stroke = PAL[pal]
        self.rect(x, y, w, h, fill, stroke, r=11)
        self.text(x + w / 2, y + 15, s, size=10.5, weight="600", anchor="middle")

    def scope(self, y, segs, role):
        """Contract-scope badge in the right column, aligned to a tier's boxes.

        Marks which phase of the one delivery touches that tier. An empty
        ``segs`` means the tier is reused or retained.
        """
        x = SCOPE_X
        if segs:
            for s in segs:
                fill, stroke = SEGPAL[s]
                self.rect(x, y, 24, 14, fill, stroke, r=4)
                self.text(x + 12, y + 10.5, {"S1": "P1", "S2": "P3", "S3": "P4", "S4": "P5"}[s],
                          size=9, weight="700", anchor="middle")
                x += 27
        else:
            self.rect(x, y, 51, 14, "#eef1f6", "#c9d3e0", r=4)
            self.text(x + 25.5, y + 10.5, "none", size=9, weight="700", fill=DIM, anchor="middle")
        self.text(SCOPE_X, y + 27, role, size=9.5, fill=DIM)

    def scope_header(self, s):
        self.text(SCOPE_X, 48, s, size=11, weight="700", fill=BAND)
        self.line(SCOPE_X, 54, SCOPE_X + SCOPE_W, 54, stroke=BAND, w=1.4)

    def tier(self, y, label, sub=""):
        """Left-gutter tier label + the horizontal bus line for that tier."""
        self.text(18, y + 4, label, size=12, weight="700", fill=BAND)
        if sub:
            self.text(18, y + 19, sub, size=10, fill=DIM)

    def bus(self, y, x0=None, x1=None, w=2.0, stroke=BAND):
        self.line(x0 if x0 is not None else CX0, y, x1 if x1 is not None else CX1, y,
                  stroke=stroke, w=w)

    def stub(self, x, y0, y1, stroke=LINE, w=1.4, dash=None):
        self.line(x, y0, x, y1, stroke=stroke, w=w, dash=dash)

    def render(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" aria-label="{esc(self.title)}">'
                f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>'
                + "".join(self.parts) + "</svg>")


def spread(n, box_w, x0=CX0, x1=CX1):
    """Evenly spaced left edges for n boxes of width box_w."""
    if n == 1:
        return [x0 + (x1 - x0 - box_w) / 2]
    gap = ((x1 - x0) - n * box_w) / (n - 1)
    return [x0 + i * (box_w + gap) for i in range(n)]


def chain_row(s, y, intro, items):
    """Terminal daisy-chain row, ending at the field devices.

    The devices genuinely hang off each panel rather than off the end of the
    chain, but a single-line diagram draws them as the terminal element -- and
    they have to appear somewhere, because they are the whole of S3's scope.
    """
    s.text(CX0, y + 18, intro, size=10.5, fill=DIM)
    cy = y + 44
    bwx, gap = 150, 34
    x = CX0
    for i, (lab, sub, dash, pal) in enumerate(items):
        s.box(x, cy, bwx, 40, lab, [sub], pal=pal, dash=dash, tsize=11)
        if i:
            s.line(x - gap, cy + 20, x, cy + 20)
        x += bwx + gap
    s.stub(CX0 + bwx / 2, y + 28, cy)
    return cy


def zone_row(s, y, note):
    """Bottom tier -- identical on both diagrams, which is the point."""
    s.tier(y + 26, "Field panels", "by cutover wave")
    s.bus(y)
    bw = (CW - 3 * 18) / 4
    for x, (name, sub, pans, pts) in zip(spread(4, bw), ZONES):
        s.stub(x + bw / 2, y, y + 16)
        s.box(x, y + 16, bw, 62, name, [sub, f"{pans} panels  ·  {pts:,} points"], pal="field")
    s.text(CX0, y + 96, note, size=10.5, fill=DIM)


# ---------------------------------------------------------------------------
# SLD 1 -- existing Azbil savic-netFX2
# ---------------------------------------------------------------------------
def build_existing():
    H = 860
    s = Svg(W, H, "Existing Azbil savic-netFX2 architecture")
    s.text(18, 30, "EXISTING — Azbil savic-netFX2 (as-built, 工番 1-LHP1-11)", size=15, weight="700", fill=BAND)
    s.text(18, 48, f"Proprietary savic-net fieldbus · {N_PANELS} RS/DDC panels · {N_POINTS:,} I/O points",
           size=11, fill=DIM)

    # --- operator tier ---
    y = 78
    s.tier(y + 26, "Operator", "監視 consoles")
    s.bus(y)
    bw = 250
    xs = spread(3, bw)
    ops = [("監視用PC1", ["Fujitsu ESPRIMO D551/G", "B2F 防災室 · panel 101"]),
           ("監視用PC2", ["Fujitsu ESPRIMO D551/G", "2F 防災センター · panel 103"]),
           ("CLP printer", ["Brother HL-4570CDW", "colour laser"])]
    for x, (t, ln) in zip(xs, ops):
        s.stub(x + bw / 2, y, y + 14)
        s.box(x, y + 14, bw, 56, t, ln, pal="ops")

    # --- server tier ---
    y = 188
    s.tier(y + 26, "Servers", "central station")
    s.bus(y)
    bw = 250
    srv = [("BMS", ["ビルマネジメントサーバ", "NEC FC-E21A"]),
           ("SMS", ["system management", "Azbil SI-net BCY45300W0020"]),
           ("DSS", ["data storage", "Azbil SI-net BCY46300W0020"])]
    for x, (t, ln) in zip(spread(3, bw), srv):
        s.stub(x + bw / 2, y, y + 14)
        s.box(x, y + 14, bw, 56, t, ln, pal="server")

    # --- ethernet backbone ---
    y = 300
    s.tier(y + 4, "Backbone", "IPv4/IPv6 Ethernet")
    s.bus(y, w=3.0)
    s.text(CX1, y - 8, "100BASE-TX · fibre risers between floors · 192.168.30.x / .31.x",
           size=10.5, fill=DIM, anchor="end")
    cw = 200
    for x, lab in zip(spread(3, cw), ["ESW1 · 8-port (panel 101)",
                                      "ESW2 · 16-port (panel 102)",
                                      "ESW3 · 8-port (panel 103)"]):
        s.stub(x + cw / 2, y, y + 12)
        s.chip(x, y + 12, cw, lab, pal="net")

    # --- SCS tier ---
    y = 382
    s.tier(y + 30, "Fieldbus head", "system-control panel 102")
    s.bus(y)
    bw = 150
    xs = spread(5, bw)
    for i, x in enumerate(xs):
        s.stub(x + bw / 2, y, y + 14)
        if i < 4:
            s.box(x, y + 14, bw, 50, f"SCS {i + 1}", ["System Core Server", "BCY44200W0000"], pal="ctrl")
        else:
            s.box(x, y + 14, bw, 50, "SCS 6", ["… ×6 total", "all on ESW2"], pal="ctrl", dash="4 3")
    s.text(CX1, y - 8, "6 × SCS — each heads up to 4 NC-bus lines → ≤24 segments",
           size=10.5, fill=DIM, anchor="end")

    # IFGD1 hangs off the same panel. Drop it straight below SCS 1 -- an L-shaped
    # connector would have to cross the box to reach its own edge.
    s.box(CX0, y + 80, 210, 44, "IFGD1", ["Inf-GD base module", "DI 16 / DO 8 — fire & external"],
          pal="legacy")
    s.stub(xs[0] + bw / 2, y + 64, y + 80)

    # --- NC-bus tier (one SCS expanded) ---
    y = 512
    s.tier(y + 26, "NC-bus", "IPEV-S 0.9 mm²")
    s.bus(y)
    s.text(CX1, y - 8, "single-line: SCS 1 expanded — same pattern ×6", size=10.5, fill=DIM, anchor="end")
    bw = 250
    for i, x in enumerate(spread(4, bw)):
        s.stub(x + bw / 2, y, y + 14)
        s.chip(x, y + 14, bw, f"NC-bus line {i + 1}  ·  TX-IN → TX-OUT", pal="net")

    # --- daisy chain of RS panels ---
    y = 576
    chain_row(s, y, "Each line is a daisy-chain of RS remote stations + DDC:", [
        ("RS-xx-1", "RS + DDC", None, "io"),
        ("RCP-xx-2", "RS + DDC", None, "io"),
        ("CP-xx-3", "RS + DDC", None, "io"),
        ("… to line end", "≤ line capacity", "4 3", "io"),
        ("Field devices", "sensors · valves · meters", None, "field"),
    ])

    # --- field zones ---
    zone_row(s, 700, f"Trunk segments (2002 伝送幹線系統図): UIC1-1/1-2 · UIC2-1…2-4 · "
                     f"UIC3-1/3-2 risers to 10F/21F/31F · UIC4-1…4-3 + UIC4-C basements. "
                     f"Totals: {N_PANELS} panels · {N_POINTS:,} points.")

    # --- what happens to each tier, by contract ---
    s.scope_header("Disposition — by phase")
    s.scope(100, ["S1"], "consoles replaced")
    s.scope(210, ["S1"], "BMS / SMS / DSS replaced")
    s.scope(306, [], "retained and reused as-is")
    s.scope(400, ["S2"], "removed, panel 102 stripped")
    s.scope(528, [], "IPEV-S cable reused")
    s.scope(624, ["S2", "S3"], "panels removed · devices replaced")
    s.scope(724, ["S2", "S3", "S4"], "worked wave by wave")
    return s.render()


# ---------------------------------------------------------------------------
# SLD 2 -- proposed Delta / Red5 BACnet
# ---------------------------------------------------------------------------
def build_proposed():
    H = 860
    s = Svg(W, H, "Proposed Delta / Red5 BACnet architecture")
    s.text(18, 30, "PROPOSED — Delta Controls / Red5 (open BACnet)", size=15, weight="700", fill="#1d6b3f")
    s.text(18, 48, f"{N_MODULES} controllers + modules · same {N_PANELS} panels · same {N_POINTS:,} points "
                   f"({N_CAP:,} capacity)", size=11, fill=DIM)

    # --- operator tier ---
    y = 78
    s.tier(y + 26, "Operator", "browser — no fat client")
    s.bus(y)
    bw = 250
    ops = [("監視用PC1", ["enteliWEB in browser", "B2F 防災室 — location retained"]),
           ("監視用PC2", ["enteliWEB in browser", "2F 防災センター — retained"]),
           ("Mobile / remote", ["read-only dashboard", "same point database"])]
    for x, (t, ln) in zip(spread(3, bw), ops):
        s.stub(x + bw / 2, y, y + 14)
        s.box(x, y + 14, bw, 56, t, ln, pal="ops")

    # --- server tier ---
    y = 188
    s.tier(y + 26, "Head-end", "replaces BMS/SMS/DSS")
    s.bus(y)
    srv = [("enteliWEB", ["supervisor · graphics", "schedules · alarms"]),
           ("Historian / DB", ["trend + periodic data", "daily/monthly reports"]),
           ("Engineering", [f"{N_DDC} GCL+ PG objects", "one per controller"])]
    for x, (t, ln) in zip(spread(3, bw), srv):
        s.stub(x + bw / 2, y, y + 14)
        s.box(x, y + 14, bw, 56, t, ln, pal="new")

    # --- backbone (reused) ---
    y = 300
    s.tier(y + 4, "Backbone", "BACnet/IP")
    s.bus(y, w=3.0, stroke="#1d6b3f")
    s.text(CX1, y - 8, "REUSED — existing switches, fibre risers and IP plan unchanged",
           size=10.5, fill="#1d6b3f", anchor="end")
    cw = 200
    for x, lab in zip(spread(3, cw), ["ESW1 · existing", "ESW2 · existing", "ESW3 · existing"]):
        s.stub(x + cw / 2, y, y + 12)
        s.chip(x, y + 12, cw, lab, pal="net")

    # --- network controller tier ---
    y = 382
    s.tier(y + 30, "Network ctrl", "replaces 6 × SCS")
    s.bus(y)
    bw = 150
    xs = spread(5, bw)
    for i, x in enumerate(xs):
        s.stub(x + bw / 2, y, y + 14)
        if i < 4:
            s.box(x, y + 14, bw, 50, "CON-T1L", ["network / BACnet", "controller"], pal="ctrl")
        else:
            s.box(x, y + 14, bw, 50, "CON-T1L", [f"… ×{N_CONT} total", "distributed in panels"],
                  pal="ctrl", dash="4 3")
    s.text(CX1, y - 8, f"{N_CONT} × CON-T1L — supervision distributed to the panels, not 6 central servers",
           size=10.5, fill=DIM, anchor="end")

    # Room controllers sit on BACnet directly, not behind an expander.
    s.box(CX0, y + 80, 260, 44, f"Red5-PLUS-ROOM ×{N_ROOM}",
          ["room controller, onboard I/O", "BACnet — guest/zone level"], pal="new")
    s.stub(xs[0] + bw / 2, y + 64, y + 80)

    # --- field bus / expander tier ---
    y = 512
    s.tier(y + 26, "Panel bus", "reuses IPEV-S routes")
    s.bus(y)
    s.text(CX1, y - 8, "single-line: one CON-T1L expanded — same pattern ×80",
           size=10.5, fill=DIM, anchor="end")
    bw = 250
    for i, x in enumerate(spread(4, bw)):
        s.stub(x + bw / 2, y, y + 14)
        lab = (f"Red5-EXPAND-04  ·  bus expander" if i < 3
               else f"… ×{N_EXPAND} expanders total")
        s.chip(x, y + 14, bw, lab, pal="net")

    # --- I/O modules ---
    y = 576
    chain_row(s, y, f"Each expander hosts I/O modules — {N_IO_MODULES} across the estate:", [
        ("4F4xP", f"×{N_M4F4}", None, "io"),
        ("8xP", f"×{N_M8}", None, "io"),
        ("8PxP", f"×{N_M8P}", None, "io"),
        ("Field wiring", "unchanged", "4 3", "field"),
        ("Field devices", f"{N_ANALOG} analog replaced", None, "new"),
    ])

    # --- field zones (identical row) ---
    zone_row(s, 700, f"Same panels, same trunk routes, same terminations — 1:1 replacement per the "
                     f"as-built drawings. Totals: {N_PANELS} panels · {N_POINTS:,} points · "
                     f"{N_CONTROLLERS} controllers + {N_EXPAND} expanders + {N_IO_MODULES} I/O modules "
                     f"= {N_MODULES} units.")

    # --- which contract delivers each tier ---
    s.scope_header("Delivered by — phase")
    s.scope(100, ["S1", "S4"], "console hardware · graphics")
    s.scope(210, ["S1", "S4"], "server hardware · software")
    s.scope(306, [], "reused — no package touches it")
    s.scope(400, ["S1", "S2", "S4"], "supply · install · program")
    s.scope(528, ["S1", "S2"], "supply · install")
    s.scope(624, ["S1", "S2", "S3"], "modules · wiring · 591 devices")
    s.scope(724, ["S2", "S3", "S4"], "installed, calibrated, proven")
    return s.render()


# ---------------------------------------------------------------------------
# comparison
# ---------------------------------------------------------------------------
COMPARE_COLS = ["Layer", "Existing — Azbil savic-netFX2", "Proposed — Delta / Red5", "Change"]
COMPARE = [
    ("Operator", "監視用PC1 (B2F 防災室) + 監視用PC2 (2F 防災センター), fat clients on ESPRIMO PCs",
     "enteliWEB in a browser at the same two locations, plus read-only remote",
     "Console locations retained; client becomes a browser"),
    ("Head-end", "BMS (NEC FC-E21A) + SMS + DSS (Azbil SI-net) — three servers",
     "enteliWEB supervisor + historian/DB",
     "Server roles consolidated"),
    ("Backbone", "IPv4/IPv6 Ethernet 100BASE-TX, fibre risers, ESW1/2/3, 192.168.30.x/.31.x",
     "Same switches, risers and IP plan, carrying BACnet/IP",
     "Reused — no network construction"),
    ("Supervision", "6 × SCS System Core Server (BCY44200W0000) in panel 102",
     f"{N_CONT} × CON-T1L network controllers distributed into the field panels",
     "Central → distributed; no single panel of failure"),
    ("Fieldbus", "≤24 NC-bus lines, IPEV-S 0.9 mm² daisy-chain, proprietary savic-net",
     "Panel bus over the same IPEV-S routes, open BACnet",
     "Proprietary → open protocol, same cable"),
    ("Field I/O", f"{N_PANELS} RS/RCP/CP panels, {N_POINTS:,} points",
     f"{N_PANELS} panels, {N_POINTS:,} points, {N_CAP:,} capacity "
     f"({N_CONTROLLERS} ctrl + {N_EXPAND} exp + {N_IO_MODULES} I/O)",
     f"1:1 replacement, {N_CAP - N_POINTS:,} spare points added"),
    ("Room level", "Guest FCUs on local thermostats, BMS sees orientation zone-groups only",
     f"Red5-PLUS-ROOM ×{N_ROOM} room controllers with onboard I/O on BACnet",
     "New capability — per-room visibility possible"),
    ("Life safety", "IFGD1 (DI 16 / DO 8) for fire alarm and external signals",
     "Equivalent hard-wired fire interface retained; BMS monitors only",
     "Unchanged by design — interlocks stay hard-wired"),
    ("Programs", "savic-netFX2 function blocks, vendor tooling",
     f"{N_DDC} GCL+ PG objects, one per controller, authored in enteliWEB",
     "Logic becomes readable and version-controllable"),
]


def write_html(path, svg_a, svg_b):
    rows = "".join(
        "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in COMPARE)
    badge = {"S1": "P1", "S2": "P3", "S3": "P4", "S4": "P5"}
    legend = "".join(
        f'<span class="lg"><i style="background:{SEGPAL[k][0]};border-color:{SEGPAL[k][1]}"></i>'
        f"<b>{badge[k]}</b> {esc(SEG_NAME[k])}</span>"
        for k in ("S1", "S2", "S3", "S4"))
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Red5-DHCP — system architecture SLD: existing vs proposed</title>
<style>
  :root {{ --ink:#1b2430; --dim:#5b6675; --line:#d8dee7; --band:#1F3864; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
          color:var(--ink); background:#f4f6f9; padding:28px; }}
  .page {{ max-width:1280px; margin:0 auto; background:#fff; border:1px solid var(--line);
           border-radius:10px; padding:28px 32px; }}
  h1 {{ font-size:22px; margin:0 0 4px; }} .sub {{ color:var(--dim); margin:0 0 18px; max-width:95ch; }}
  h2 {{ font-size:16px; margin:26px 0 8px; border-bottom:2px solid var(--band); padding-bottom:4px; color:var(--band); }}
  .dia {{ border:1px solid var(--line); border-radius:8px; padding:8px; margin:10px 0 6px; overflow-x:auto; }}
  .dia svg {{ display:block; width:100%; height:auto; min-width:1000px; }}
  table {{ border-collapse:collapse; width:100%; margin:6px 0; font-size:13px; }}
  th, td {{ border:1px solid var(--line); padding:7px 9px; text-align:left; vertical-align:top; }}
  thead th {{ background:var(--band); color:#fff; }}
  tbody tr td:first-child {{ font-weight:700; white-space:nowrap; }}
  .note {{ color:var(--dim); font-size:12px; margin:4px 0 0; }}
  .legend {{ display:flex; gap:18px; flex-wrap:wrap; margin:10px 0 4px; font-size:12.5px; }}
  .lg {{ display:inline-flex; align-items:center; gap:6px; }}
  .lg i {{ width:14px; height:14px; border-radius:4px; border:1.5px solid; display:inline-block; }}
  .foot {{ color:var(--dim); font-size:12px; margin-top:22px; }}
  @media print {{ body {{ background:#fff; padding:0; }} .page {{ border:0; }}
                  .dia {{ break-inside:avoid; page-break-inside:avoid; }} }}
</style></head>
<body><div class="page">
<h1>Red5-DHCP — system architecture single-line diagrams</h1>
<p class="sub">ANA InterContinental Tokyo BMS retrofit: the existing Azbil savic-netFX2 architecture and the
proposed Delta&nbsp;/&nbsp;Red5 BACnet replacement, drawn on the same tier skeleton so the swap reads at a
glance. One representative branch is expanded per tier with its multiplicity annotated — drawing all
{N_PANELS} panels would make it a wiring diagram.</p>
<p class="sub">Both diagrams carry a right-hand <b>phase column</b> for the one continuous delivery:
P1 fabrication, P3 installation, P4 instruments, P5 programming. Tiers marked <b>none</b> are reused
or retained.</p>
<div class="legend">{legend}</div>

<h2>1 · Existing — Azbil savic-netFX2 (as-built)</h2>
<div class="dia">{svg_a}</div>
<p class="note">Basis: savic-netFX2 ESCO hardware delivery spec 工番 1-LHP1-11 (drawings LHP1-11-200-01/02,
-100-B0xx, -202-xx) and the 2002 伝送幹線系統図 trunk drawing. See docs/reconciliation_2026-08.md §2–3.</p>

<h2>2 · Proposed — Delta Controls / Red5 (open BACnet)</h2>
<div class="dia">{svg_b}</div>
<p class="note">Basis: the {N_MODULES}-unit controller and module fleet in panels_schedule.json
({SRC}), typed on the Delta-Controllers sheet of Red5-DHCP_BMS_IO_List.xlsx. The bottom tier is identical
to diagram 1 — that is the 1:1 replacement claim, shown rather than asserted.</p>

<h2>3 · Existing vs new — layer by layer</h2>
<table><thead><tr>{"".join(f"<th>{esc(c)}</th>" for c in COMPARE_COLS)}</tr></thead>
<tbody>{rows}</tbody></table>

<p class="foot">Generated {TODAY} · Red5-DHCP · sources: panels_schedule.json (판넬별 포인트 정리 {SRC}),
docs/reconciliation_2026-08.md, generate_io_list.py (Delta-Controllers sheet). Regenerate with
<code>.venv/bin/python build_sld.py</code>. Print to PDF for distribution.</p>
</div></body></html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


if __name__ == "__main__":
    os.makedirs(EXPORT_DIR, exist_ok=True)
    svg_a = build_existing()
    svg_b = build_proposed()
    with open(os.path.join(EXPORT_DIR, "red5-dhcp_sld-existing.svg"), "w", encoding="utf-8") as f:
        f.write(svg_a)
    with open(os.path.join(EXPORT_DIR, "red5-dhcp_sld-proposed.svg"), "w", encoding="utf-8") as f:
        f.write(svg_b)
    write_html(os.path.join(EXPORT_DIR, "red5-dhcp_sld.html"), svg_a, svg_b)

    # Both diagrams must describe the same building.
    zp = sum(z[2] for z in ZONES)
    zpt = sum(z[3] for z in ZONES)
    assert zp == N_PANELS, (zp, N_PANELS)
    assert zpt == N_POINTS, (zpt, N_POINTS)
    assert N_CONTROLLERS + N_EXPAND + N_IO_MODULES == N_MODULES, N_MODULES
    print(f"SLDs exported: existing + proposed, {N_PANELS} panels / {N_POINTS:,} points, "
          f"{N_MODULES} units -> exports/red5-dhcp_sld-{{existing,proposed}}.svg + red5-dhcp_sld.html")
