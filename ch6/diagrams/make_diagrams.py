"""Inline-SVG diagrams for Ch.6 (block diagrams and simplified P&IDs).

Writes one Quarto include per diagram:  diagrams/_<name>.md  (```{=html} <svg> ```).
Same visual language as ch4/diagrams/_decision_chart.md.
    python diagrams/make_diagrams.py
"""
import re
from pathlib import Path

OUT = Path(__file__).parent
NAVY, RED, GREEN, GRAY, INK = "#333399", "#C00000", "#2E7D32", "#888888", "#222"


def mtxt(s):
    """Tiny math markup:  G_{c2}  X^{*}  ->  SVG tspans (dy-based, works in every browser)."""
    out, i = [], 0
    for m in re.finditer(r"([_^])\{([^}]*)\}", s):
        out.append(s[i:m.start()])
        dy = "0.32em" if m.group(1) == "_" else "-0.45em"
        back = "-0.32em" if m.group(1) == "_" else "0.45em"
        out.append(f'<tspan dy="{dy}" font-size="72%">{m.group(2)}</tspan><tspan dy="{back}">​</tspan>')
        i = m.end()
    out.append(s[i:])
    return "".join(out)


class SVG:
    def __init__(self, name, w, h, label):
        self.name, self.w, self.h, self.label, self.el = name, w, h, label, []
        self.p = re.sub(r"\W", "", name)

    # ---------------------------------------------------------- primitives
    def wire(self, pts, arrow=True, dash=False, color="#555", width=2):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        extra = f' stroke-dasharray="6 5"' if dash else ""
        mk = f' marker-end="url(#{self.p}-arr)"' if arrow else ""
        self.el.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{extra}{mk}/>')

    def signal(self, pts, arrow=True):            # instrument signal line (dashed)
        self.wire(pts, arrow=arrow, dash=True, color=NAVY, width=1.6)

    def pipe(self, pts, arrow=True):              # process line
        self.wire(pts, arrow=arrow, color=INK, width=2.4)

    def box(self, cx, cy, label, w=104, h=56, kind="box", size=24):
        cls = {"box": 'fill="#fff" stroke="%s" stroke-width="2"' % NAVY,
               "meth": f'fill="{NAVY}"',
               "soft": 'fill="#eef0fa" stroke="%s" stroke-width="2"' % NAVY,
               "red": 'fill="#fff4f4" stroke="%s" stroke-width="2"' % RED,
               "ghost": 'fill="#fafafa" stroke="#bbb" stroke-width="1.6" stroke-dasharray="6 4"'}[kind]
        self.el.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="8" {cls} '
                       f'filter="url(#{self.p}-sh)"/>')
        col = "#fff" if kind == "meth" else (GRAY if kind == "ghost" else INK)
        self.math(cx, cy, label, size=size, color=col)
        return dict(l=(cx - w / 2, cy), r=(cx + w / 2, cy), t=(cx, cy - h / 2), b=(cx, cy + h / 2))

    def sumj(self, cx, cy, signs, r=13):
        self.el.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="2"/>')
        off = {"w": (-r - 9, -r + 2), "n": (r + 4, -r - 5), "s": (r + 4, r + 16), "e": (r + 4, -r)}
        for side, sg in signs.items():
            dx, dy = off[side]
            self.el.append(f'<text x="{cx + dx}" y="{cy + dy}" font-size="19" font-weight="700" '
                           f'text-anchor="middle" fill="{INK}">{sg}</text>')
        return dict(l=(cx - r, cy), r=(cx + r, cy), t=(cx, cy - r), b=(cx, cy + r))

    def dot(self, x, y):
        self.el.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{INK}"/>')

    def math(self, x, y, s, size=22, color=INK, anchor="middle", italic=True):
        st = "italic" if italic else "normal"
        self.el.append(f'<text x="{x}" y="{y}" font-family="\'Times New Roman\', \'STIX Two Text\', serif" '
                       f'font-style="{st}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
                       f'dominant-baseline="central">{mtxt(s)}</text>')

    def text(self, x, y, s, size=17, color="#444", anchor="middle", weight=400, italic=False):
        st = ' font-style="italic"' if italic else ""
        self.el.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
                       f'font-weight="{weight}" dominant-baseline="central"{st}>{mtxt(s)}</text>')

    def bubble(self, cx, cy, tag, r=21):
        self.el.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{NAVY}" stroke-width="2"/>')
        self.text(cx, cy + 1, tag, size=15, color=NAVY, weight=700)
        return dict(l=(cx - r, cy), r=(cx + r, cy), t=(cx, cy - r), b=(cx, cy + r))

    def valve(self, cx, cy, s=13):
        self.el.append(f'<path d="M{cx - s},{cy - s * 0.8} L{cx + s},{cy + s * 0.8} L{cx + s},{cy - s * 0.8} '
                       f'L{cx - s},{cy + s * 0.8} Z" fill="#fff" stroke="{INK}" stroke-width="2"/>')
        self.el.append(f'<path d="M{cx},{cy} L{cx},{cy - 22} M{cx - 12},{cy - 22} A12,12 0 0 1 {cx + 12},{cy - 22} Z" '
                       f'fill="#fff" stroke="{INK}" stroke-width="2"/>')
        return (cx, cy - 34)                       # actuator top (signal goes here)

    def raw(self, s):
        self.el.append(s)

    # ---------------------------------------------------------- output
    def write(self):
        svg = (f'<svg class="bdia" viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" role="img" '
               f'aria-label="{self.label}">\n'
               f'  <defs>\n'
               f'    <marker id="{self.p}-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
               f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker>\n'
               f'    <filter id="{self.p}-sh" x="-10%" y="-10%" width="130%" height="140%"><feDropShadow dx="0" '
               f'dy="2" stdDeviation="2.5" flood-color="{NAVY}" flood-opacity="0.16"/></filter>\n'
               f'  </defs>\n'
               f'  <style>.bdia{{width:100%;height:auto;font-family:inherit}} .bdia text{{font-family:inherit}}</style>\n  '
               + "\n  ".join(self.el) + "\n</svg>")
        (OUT / f"_{self.name}.md").write_text("```{=html}\n" + svg + "\n```\n")
        return svg


# =================================================================== diagrams
def cascade_block():
    d = SVG("cascade_block", 980, 270, "Block diagram of a cascade control system")
    y = 140
    d.math(22, y - 22, "R", anchor="middle")
    s1 = d.sumj(70, y, {"w": "+", "s": "−"})
    gc = d.box(175, y, "G_{c}", w=90)
    s2 = d.sumj(300, y, {"w": "+", "s": "−"})
    gc2 = d.box(395, y, "G_{c2}", w=90)
    gv = d.box(520, y, "G_{v}", w=90)
    s3 = d.sumj(630, y, {"w": "+", "n": "+"})
    gl = d.box(630, 58, "G_{L}", w=86, h=50)
    gp = d.box(790, y, "G_{p}", w=90)
    d.wire([(8, y), s1["l"]]); d.wire([s1["r"], gc["l"]]); d.wire([gc["r"], s2["l"]])
    d.wire([s2["r"], gc2["l"]]); d.wire([gc2["r"], gv["l"]]); d.wire([gv["r"], s3["l"]])
    d.wire([s3["r"], gp["l"]]); d.wire([gp["r"], (960, y)])
    d.wire([(630, 4), gl["t"]]); d.wire([gl["b"], s3["t"]])
    d.math(648, 12, "L", anchor="start")
    d.text(675, 22, "upstream fuel-gas pressure", size=15, color=RED, anchor="start")
    d.math(105, y - 20, "E"); d.math(250, y - 20, "p"); d.math(338, y - 20, "e_{2}"); d.math(690, y - 20, "a")
    d.math(945, y - 22, "C")
    d.dot(700, y); d.wire([(700, y), (700, 200), (300, 200), s2["b"]])
    d.text(500, 215, "inner (slave) loop: fuel-gas flow", size=15, color=GREEN)
    d.dot(905, y); d.wire([(905, y), (905, 250), (70, 250), s1["b"]])
    d.text(500, 262, "outer (master) loop: temperature", size=15, color=NAVY)
    d.write()


def cascade_reduced():
    d = SVG("cascade_reduced", 820, 190, "Reduced block diagram of a cascade system")
    y = 110
    d.math(22, y - 22, "R")
    s1 = d.sumj(70, y, {"w": "+", "s": "−"})
    gc = d.box(180, y, "G_{c}", w=90)
    gv = d.box(320, y, "G_{v}^{*}", w=96, kind="soft")
    s3 = d.sumj(440, y, {"w": "+", "n": "+"})
    gl = d.box(440, 38, "G_{L}^{*}", w=86, h=46, kind="soft")
    gp = d.box(575, y, "G_{p}", w=90)
    d.wire([(8, y), s1["l"]]); d.wire([s1["r"], gc["l"]]); d.wire([gc["r"], gv["l"]])
    d.wire([gv["r"], s3["l"]]); d.wire([s3["r"], gp["l"]]); d.wire([gp["r"], (800, y)])
    d.wire([(530, 4), (530, 38), gl["r"]], arrow=True) if False else None
    d.wire([(440, -2), gl["t"]]) if False else None
    d.wire([(380, 38), gl["l"]]); d.math(366, 38, "L", anchor="end")
    d.wire([gl["b"], s3["t"]])
    d.math(785, y - 22, "C")
    d.dot(690, y); d.wire([(690, y), (690, 170), (70, 170), s1["b"]])
    d.text(320, 158, "slave loop collapsed into G_{v}^{*}, G_{L}^{*}", size=15, color=GREEN)
    d.write()


def ff_fb(fb=True):
    name = "fffb_block" if fb else "ff_block"
    d = SVG(name, 980, 300, "Feedforward-feedback block diagram" if fb else "Feedforward block diagram")
    y = 190
    k = "box" if fb else "ghost"
    if fb:
        d.math(22, y - 22, "R")
        s1 = d.sumj(70, y, {"w": "+", "s": "−"})
        d.wire([(8, y), s1["l"]]); d.math(110, y - 20, "E")
    gc = d.box(185, y, "G_{c}", w=90, kind=k)
    s2 = d.sumj(310, y, {"w": "+", "n": "+"})
    gv = d.box(420, y, "G_{v}^{*}", w=96)
    gp = d.box(575, y, "G_{p}", w=90)
    s3 = d.sumj(705, y, {"w": "+", "n": "+"})
    gml = d.box(505, 44, "G_{mL}", w=96, h=48, kind="red")
    gff = d.box(310, 108, "G_{FF}", w=96, h=50, kind="red")
    gl = d.box(705, 108, "G_{L}", w=86, h=50)
    if fb:
        d.wire([s1["r"], gc["l"]])
    d.wire([gc["r"], s2["l"]], dash=not fb, color="#555" if fb else "#bbb")
    d.wire([s2["r"], gv["l"]]); d.wire([gv["r"], gp["l"]]); d.math(500, y - 20, "M")
    d.wire([gp["r"], s3["l"]]); d.wire([s3["r"], (960, y)]); d.math(945, y - 22, "C")
    d.wire([(705, 6), gl["t"]]); d.math(722, 14, "L", anchor="start")
    d.text(745, 16, "measured disturbance", size=15, color=RED, anchor="start")
    d.dot(705, 44); d.wire([(705, 44), gml["r"]]); d.wire([gml["l"], (310, 44), gff["t"]])
    d.wire([gff["b"], s2["t"]]); d.wire([gl["b"], s3["t"]])
    if fb:
        gm = d.box(505, 268, "G_{m}", w=90, h=46)
        d.dot(850, y); d.wire([(850, y), (850, 268), gm["r"]]); d.wire([gm["l"], (70, 268), s1["b"]])
        d.text(250, 252, "feedback: corrects model error", size=15, color=NAVY)
    else:
        d.wire([(850, y), (850, 262), (185, 262), gc["b"]], dash=True, color="#bbb")
        d.text(505, 280, "feedback loop (added in §6.3)", size=15, color=GRAY)
    d.text(160, 80, "feedforward:", size=15, color=RED, anchor="middle")
    d.text(160, 100, "acts before C moves", size=15, color=RED, anchor="middle")
    d.write()


def furnace(name, ff=False):
    """Fired heater: cascade temperature control (ff=False), plus feedforward from the process stream (ff=True)."""
    H = 490 if ff else 450
    d = SVG(name, 980, H, "Furnace temperature control" + (" with feedforward, feedback and cascade" if ff else " with cascade"))
    fx, fy, fw, fh = 330, 120, 170, 240
    # stack, hood and fire box
    d.raw(f'<path d="M{fx + 60},{fy - 40} L{fx + 60},{fy - 62} M{fx + 110},{fy - 62} L{fx + 110},{fy - 40}" '
          f'fill="none" stroke="{INK}" stroke-width="2.4"/>')
    d.raw(f'<path d="M{fx},{fy} L{fx + 60},{fy - 40} L{fx + 110},{fy - 40} L{fx + fw},{fy} Z" fill="#f7f7fb" '
          f'stroke="{INK}" stroke-width="2.4"/>')
    d.raw(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="#f7f7fb" stroke="{INK}" stroke-width="2.4"/>')
    d.text(fx + fw / 2, fy + fh - 20, "furnace", size=16, color="#555")
    pts, yy = [], fy + 40
    for i in range(5):
        pts += [(fx + 30, yy), (fx + 140, yy)] if i % 2 == 0 else [(fx + 140, yy), (fx + 30, yy)]
        yy += 26
    d.raw('<path d="M' + " L".join(f"{x},{y}" for x, y in pts) + f'" fill="none" stroke="{NAVY}" stroke-width="2.4"/>')
    for i in range(5):
        bx = fx + 45 + i * 20
        d.raw(f'<path d="M{bx - 7},{fy + fh - 42} L{bx},{fy + fh - 58} L{bx + 7},{fy + fh - 42}" fill="none" '
              f'stroke="{RED}" stroke-width="1.8"/>')
    inlet_y = fy + 40 + 4 * 26                      # bottom pass of the coil (enters here)
    d.pipe([(24, inlet_y), (fx + 30, inlet_y)], arrow=True)
    d.text(24, inlet_y + 22, "cold process stream", size=15, anchor="start")
    d.pipe([(fx + 140, fy + 40), (fx + fw + 24, fy + 40), (fx + fw + 24, 32), (960, 32)], arrow=True)
    d.text(830, 14, "hot process stream", size=16)
    d.math(570, 14, "T", size=22)
    tt = d.bubble(620, 92, "TT"); d.signal([(620, 32), tt["t"]], arrow=False)
    tc = d.bubble(730, 92, "TC"); d.signal([tt["r"], tc["l"]])
    d.math(802, 92, "T^{s}", size=22); d.signal([(786, 92), tc["r"]])
    fl = fy + fh + 60                                 # fuel line
    vx = 640
    d.pipe([(960, fl), (vx + 14, fl)], arrow=False)
    act = d.valve(vx, fl)
    d.pipe([(vx - 14, fl), (fx + fw / 2, fl), (fx + fw / 2, fy + fh)], arrow=True)
    d.text(910, fl + 22, "fuel gas", size=16)
    ft = d.bubble(830, fl - 56, "FT"); d.signal([(830, fl), ft["b"]], arrow=False)
    fc = d.bubble(730, fl - 116, "FC")
    d.signal([ft["l"], (780, fl - 56), (780, fl - 116), fc["r"]])
    d.signal([fc["b"], (730, fl - 62), (vx, fl - 62), act])
    if not ff:
        d.signal([tc["b"], fc["t"]])
        d.text(745, 190, "TC output = FC set point", size=15, color=GREEN, anchor="start")
        d.text(845, fl - 116, "slave loop", size=15, color=GREEN, anchor="start")
    else:
        sig = d.bubble(730, 200, "Σ")
        d.signal([tc["b"], sig["t"]]); d.signal([sig["b"], fc["t"]])
        ttin = d.bubble(120, inlet_y - 80, "TT"); d.signal([(120, inlet_y), ttin["b"]], arrow=False)
        ftin = d.bubble(250, inlet_y - 80, "FT"); d.signal([(250, inlet_y), ftin["b"]], arrow=False)
        ffc = d.bubble(185, inlet_y - 160, "FFC")
        d.signal([ttin["t"], (120, inlet_y - 160), ffc["l"]]); d.signal([ftin["t"], (250, inlet_y - 160), ffc["r"]], arrow=False)
        d.signal([(250, inlet_y - 160), ffc["r"]])
        d.signal([ffc["t"], (185, 200 - 0), (185, 200)], arrow=False) if False else None
        d.signal([(185, inlet_y - 181), (185, 46), (560, 46), (560, 200), sig["l"]])
        d.text(96, inlet_y - 112, "inlet T", size=14, color=RED, anchor="end")
        d.text(274, inlet_y - 112, "inlet flow", size=14, color=RED, anchor="start")
        d.text(250, 66, "feedforward signal", size=15, color=RED)
        d.text(760, 200, "FB + FF → FC set point", size=14, color=NAVY, anchor="start")
    d.write()


def ratio():
    d = SVG("ratio", 1000, 340, "Simple and full-metering ratio control")
    # (a) simple ratio
    d.text(20, 18, "(a) simple ratio control", size=17, color=RED, anchor="start", weight=700)
    d.pipe([(20, 80), (440, 80)]); d.text(230, 60, "fuel gas (wild stream) F_{FG}", size=15)
    ft1 = d.bubble(110, 140, "FT"); d.signal([(110, 80), ft1["t"]], arrow=False)
    rs = d.bubble(220, 140, "RS"); d.signal([ft1["r"], rs["l"]])
    d.text(262, 132, "ratio station", size=14, color=NAVY, anchor="start")
    d.math(262, 158, "F_{A}^{s} = R F_{FG}", size=18, anchor="start", color=NAVY)
    fc = d.bubble(220, 215, "FC"); d.signal([rs["b"], fc["t"]])
    d.pipe([(440, 290), (234, 290)], arrow=False); act = d.valve(220, 290)
    d.pipe([(206, 290), (20, 290)]); d.text(330, 310, "air F_{A}", size=15)
    ft2 = d.bubble(110, 215, "FT"); d.signal([(110, 290), ft2["b"]], arrow=False)
    d.signal([ft2["r"], fc["l"]]); d.signal([fc["b"], act])
    # (b) full metering
    ox = 520
    d.text(ox, 18, "(b) full-metering ratio control", size=17, color=RED, anchor="start", weight=700)
    sg = d.bubble(ox + 120, 60, "Σ"); d.text(ox + 150, 50, "set point from the FF–FB loops", size=14, color=NAVY, anchor="start")
    fc1 = d.bubble(ox + 120, 120, "FC"); d.signal([sg["b"], fc1["t"]])
    d.pipe([(ox + 460, 190), (ox + 134, 190)], arrow=False); a1 = d.valve(ox + 120, 190)
    d.pipe([(ox + 106, 190), (ox, 190)]); d.text(ox + 330, 172, "fuel gas → furnace", size=15)
    ft3 = d.bubble(ox + 230, 120, "FT"); d.signal([(ox + 230, 190), ft3["b"]], arrow=False)
    d.signal([ft3["l"], fc1["r"]]); d.signal([fc1["b"], a1])
    rc = d.bubble(ox + 330, 252, "RC"); d.signal([ft3["r"], (ox + 420, 120), (ox + 420, 252), rc["r"]])
    d.math(ox + 348, 214, "R", size=20, anchor="start"); d.signal([(ox + 330, 206), rc["t"]])
    fc2 = d.bubble(ox + 200, 252, "FC"); d.signal([rc["l"], fc2["r"]])
    d.pipe([(ox + 460, 310), (ox + 214, 310)], arrow=False); a2 = d.valve(ox + 200, 310)
    d.pipe([(ox + 186, 310), (ox, 310)]); d.text(ox + 360, 294, "air → furnace", size=15)
    ft4 = d.bubble(ox + 90, 252, "FT"); d.signal([(ox + 90, 310), ft4["b"]], arrow=False)
    d.signal([ft4["r"], fc2["l"]]); d.signal([fc2["b"], a2])
    d.write()


def smith():
    d = SVG("smith", 1000, 420, "Smith predictor")
    d.text(20, 18, "(a) feedback with dead time", size=16, color=RED, anchor="start", weight=700)
    y = 70
    d.math(20, y - 22, "R"); s = d.sumj(70, y, {"w": "+", "s": "−"})
    gc = d.box(180, y, "G_{c}(s)", w=110, h=50); gp = d.box(360, y, "G(s)e^{−θs}", w=150, h=50)
    d.wire([(6, y), s["l"]]); d.wire([s["r"], gc["l"]]); d.wire([gc["r"], gp["l"]]); d.wire([gp["r"], (520, y)])
    d.math(508, y - 22, "Y"); d.dot(480, y); d.wire([(480, y), (480, 118), (70, 118), s["b"]])
    d.text(560, y, "1 + G_{c}Ge^{−θs} = 0: delay in the loop", size=16, color=NAVY, anchor="start")
    # (b) Smith predictor
    d.text(20, 160, "(b) Smith predictor (dead-time compensator)", size=16, color=RED, anchor="start", weight=700)
    y = 300
    d.math(20, y - 22, "R"); s = d.sumj(70, y, {"w": "+", "n": "−", "s": "−"})
    gc = d.box(200, y, "G_{c}(s)", w=110, h=50); gp = d.box(420, y, "G(s)e^{−θs}", w=150, h=50)
    comp = d.box(240, 210, "G(s)(1 − e^{−θs})", w=210, h=50, kind="red")
    d.wire([(6, y), s["l"]]); d.wire([s["r"], gc["l"]]); d.math(110, y - 20, "E"); d.wire([gc["r"], gp["l"]])
    d.wire([gp["r"], (600, y)]); d.math(588, y - 22, "Y")
    d.dot(300, y); d.wire([(300, y), (380, y)], arrow=False) if False else None
    d.wire([(300, y), (300, 260), (360, 260), (360, 210), comp["r"]]) if False else d.wire([(300, y), (390, y - 0)], arrow=False) if False else None
    d.dot(300, y); d.wire([(300, y), (300, 248)], arrow=False); d.wire([(300, 248), (390, 248), (390, 210), comp["r"]])
    d.wire([comp["l"], (70, 210), s["t"]])
    d.dot(550, y); d.wire([(550, y), (550, 360), (70, 360), s["b"]])
    # (c) equivalent
    ox = 625
    d.text(ox, 160, "(c) equivalent loop", size=16, color=RED, anchor="start", weight=700)
    y = 250
    d.math(ox, y - 22, "R"); s = d.sumj(ox + 40, y, {"w": "+", "s": "−"})
    gc = d.box(ox + 120, y, "G_{c}", w=70, h=46); g = d.box(ox + 210, y, "G", w=60, h=46)
    dl = d.box(ox + 305, y, "e^{−θs}", w=80, h=46, kind="soft")
    d.wire([(ox - 12, y), s["l"]]); d.wire([s["r"], gc["l"]]); d.wire([gc["r"], g["l"]]); d.wire([g["r"], dl["l"]])
    d.wire([dl["r"], (ox + 368, y)]); d.math(ox + 356, y - 24, "Y")
    d.dot(ox + 254, y); d.wire([(ox + 254, y), (ox + 254, 300), (ox + 40, 300), s["b"]])
    d.text(ox + 180, 330, "delay moved outside the loop", size=15, color=GREEN)
    d.text(ox + 180, 352, "char. eq.  1 + G_{c}G = 0", size=15, color=GREEN)
    d.write()


def blending():
    d = SVG("blending", 1000, 330, "Blending process and its 2x2 transfer-function model")
    # process
    d.pipe([(20, 70), (160, 70)], arrow=False); a1 = d.valve(174, 70); d.pipe([(188, 70), (300, 70), (300, 180)], arrow=True)
    d.math(110, 48, "m_{1}", size=20); d.text(110, 96, "pure A", size=14, color="#666")
    d.pipe([(20, 200), (160, 200)], arrow=False); a2 = d.valve(174, 200)
    d.pipe([(188, 200), (470, 200)], arrow=True); d.math(110, 178, "m_{2}", size=20)
    d.text(110, 224, "solvent", size=14, color="#666")
    ft = d.bubble(380, 140, "FT"); ct_ = d.bubble(450, 140, "CT")
    d.signal([(380, 200), ft["b"]], arrow=False); d.signal([(450, 200), ct_["b"]], arrow=False)
    fc = d.bubble(380, 70, "FC"); cc = d.bubble(450, 70, "CC")
    d.signal([ft["t"], fc["b"]]); d.signal([ct_["t"], cc["b"]])
    d.math(398, 104, "F", size=18, anchor="start"); d.math(468, 104, "x", size=18, anchor="start")
    d.text(250, 290, "control total flow F and composition x", size=15, color=NAVY)
    d.text(250, 312, "with the two valve flows m_{1}, m_{2}", size=15, color=NAVY)
    # 2x2 block model
    ox = 560
    for i, (lab, yy) in enumerate([("G_{11}", 60), ("G_{12}", 130), ("G_{21}", 200), ("G_{22}", 270)]):
        d.box(ox + 200, yy, lab, w=86, h=48)
    s1 = d.sumj(ox + 330, 60, {"w": "+", "s": "+"}); s2 = d.sumj(ox + 330, 270, {"w": "+", "n": "+"})
    d.math(ox + 10, 38, "M_{1}"); d.math(ox + 10, 248, "M_{2}")
    d.wire([(ox, 60), (ox + 157, 60)]); d.dot(ox + 70, 60); d.wire([(ox + 70, 60), (ox + 70, 200), (ox + 157, 200)])
    d.wire([(ox, 270), (ox + 157, 270)]); d.dot(ox + 110, 270); d.wire([(ox + 110, 270), (ox + 110, 130), (ox + 157, 130)])
    d.wire([(ox + 243, 60), s1["l"]]); d.wire([(ox + 243, 130), (ox + 330, 130), s1["b"]])
    d.wire([(ox + 243, 270), s2["l"]]); d.wire([(ox + 243, 200), (ox + 330, 200), s2["t"]])
    d.wire([s1["r"], (ox + 430, 60)]); d.wire([s2["r"], (ox + 430, 270)])
    d.math(ox + 400, 38, "C_{1} = x"); d.math(ox + 400, 248, "C_{2} = F")
    d.write()


def mimo(decouple=False):
    name = "decoupling" if decouple else "mimo_loops"
    d = SVG(name, 1000, 420, "2x2 multiloop control" + (" with feedforward-like decouplers" if decouple else ""))
    y1, y2 = 90, 330
    ox = 520 if decouple else 430
    # controllers
    d.math(20, y1 - 22, "R_{1}"); s1 = d.sumj(70, y1, {"w": "+", "n": "−"})
    d.math(20, y2 - 22, "R_{2}"); s2 = d.sumj(70, y2, {"w": "+", "s": "−"})
    c1 = d.box(165, y1, "G_{c1}", w=86, h=50); c2 = d.box(165, y2, "G_{c2}", w=86, h=50)
    d.wire([(6, y1), s1["l"]]); d.wire([s1["r"], c1["l"]]); d.wire([(6, y2), s2["l"]]); d.wire([s2["r"], c2["l"]])
    if decouple:
        a1 = d.sumj(400, y1, {"w": "+", "s": "+"}); a2 = d.sumj(400, y2, {"w": "+", "n": "+"})
        d21 = d.box(300, 170, "D_{21}", w=80, h=46, kind="red"); d12 = d.box(300, 250, "D_{12}", w=80, h=46, kind="red")
        d.wire([c1["r"], a1["l"]]); d.wire([c2["r"], a2["l"]])
        d.dot(240, y1); d.wire([(240, y1), (240, 170), d21["l"]]); d.wire([d21["r"], (400, 170), a2["t"]])
        d.dot(240, y2); d.wire([(240, y2), (240, 250), d12["l"]]); d.wire([d12["r"], (380, 250), (380, 150), (400, 150), a1["b"]]) if False else d.wire([d12["r"], (360, 250), (360, 130), (400, 130), a1["b"]])
        m1x, m2x = a1["r"], a2["r"]
        d.math(450, y1 - 22, "M_{1}"); d.math(450, y2 - 22, "M_{2}")
    else:
        m1x, m2x = c1["r"], c2["r"]
        d.math(300, y1 - 22, "M_{1}"); d.math(300, y2 - 22, "M_{2}")
    # process
    g11 = d.box(ox + 200, y1, "G_{11}", w=86, h=48); g12 = d.box(ox + 200, 170, "G_{12}", w=86, h=48)
    g21 = d.box(ox + 200, 250, "G_{21}", w=86, h=48); g22 = d.box(ox + 200, y2, "G_{22}", w=86, h=48)
    o1 = d.sumj(ox + 320, y1, {"w": "+", "s": "+"}); o2 = d.sumj(ox + 320, y2, {"w": "+", "n": "+"})
    d.wire([m1x, g11["l"]]); d.dot(ox + 70, y1); d.wire([(ox + 70, y1), (ox + 70, 250), g21["l"]])
    d.wire([m2x, g22["l"]]); d.dot(ox + 110, y2); d.wire([(ox + 110, y2), (ox + 110, 170), g12["l"]])
    d.wire([g11["r"], o1["l"]]); d.wire([g12["r"], (ox + 320, 170), o1["b"]])
    d.wire([g22["r"], o2["l"]]); d.wire([g21["r"], (ox + 320, 250), o2["t"]])
    end = min(ox + 460, 990)
    d.wire([o1["r"], (end, y1)]); d.wire([o2["r"], (end, y2)])
    d.math(end - 14, y1 - 22, "C_{1}"); d.math(end - 14, y2 - 22, "C_{2}")
    d.dot(end - 40, y1); d.wire([(end - 40, y1), (end - 40, 26), (70, 26), s1["t"]])
    d.dot(end - 40, y2); d.wire([(end - 40, y2), (end - 40, 396), (70, 396), s2["b"]])
    if decouple:
        d.text(ox + 330, 150, "D_{12} cancels G_{12}:  G_{12} + G_{11}D_{12} = 0", size=14, color=RED, anchor="start") if False else None
    d.write()


if __name__ == "__main__":
    for f in (cascade_block, cascade_reduced, lambda: ff_fb(False), lambda: ff_fb(True),
              lambda: furnace("furnace_cascade"), lambda: furnace("furnace_full", ff=True),
              ratio, smith, blending, lambda: mimo(False), lambda: mimo(True)):
        f()
    print("diagrams written:", sorted(p.name for p in OUT.glob("_*.md")))
