"""Inline-SVG diagrams for Ch.2 (uses the shared helper tools/svgdiagram.py).
    python diagrams/make_diagrams.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from svgdiagram import SVG, NAVY, RED, GREEN, GRAY, INK  # noqa: E402

LIQ = "#e6eefc"


def S(name, w, h, label):
    return SVG(name, w, h, label, out=HERE)


def bowtie(d, cx, cy, s=13):
    """Hand valve (no actuator)."""
    d.raw(f'<path d="M{cx - s},{cy - s * 0.8} L{cx + s},{cy + s * 0.8} L{cx + s},{cy - s * 0.8} '
          f'L{cx - s},{cy + s * 0.8} Z" fill="#fff" stroke="{INK}" stroke-width="2"/>')


def tbox(d, cx, cy, txt, w=150, h=54, sub=None, kind="box"):
    """Box carrying a plain-text label (hardware names)."""
    b = d.box(cx, cy, "", w=w, h=h, kind=kind)
    if sub:
        d.text(cx, cy - 10, txt, size=16, color=INK, weight=600); d.text(cx, cy + 13, sub, size=13, color=GRAY)
    else:
        d.text(cx, cy, txt, size=16, color=INK, weight=600)
    return b


def tank(d, x0, x1, y0, y1, ylev):
    d.raw(f'<rect x="{x0 + 2}" y="{ylev}" width="{x1 - x0 - 4}" height="{y1 - ylev - 2}" fill="{LIQ}"/>')
    waves = " ".join(f"Q{x + 8},{ylev - 5} {x + 16},{ylev}" for x in range(x0 + 4, x1 - 16, 16))
    d.raw(f'<path d="M{x0 + 4},{ylev} {waves}" fill="none" stroke="{NAVY}" stroke-width="1.2"/>')
    d.raw(f'<path d="M{x0},{y0} L{x0},{y1} L{x1},{y1} L{x1},{y0}" fill="none" stroke="{INK}" stroke-width="2.6"/>')


# --------------------------------------------------------------------------- 2.1
def level_loop():
    d = S("level_loop", 1000, 300, "Liquid-level feedback loop and its block diagram")
    tank(d, 60, 300, 50, 262, 110)
    d.pipe([(10, 30), (180, 30), (180, 96)]); d.math(30, 52, "q_{i}", size=20)
    d.math(180, 180, "h", size=24, color=NAVY); d.wire([(200, 112), (200, 258)], color=NAVY, width=1.4)
    d.wire([(200, 258), (200, 112)], color=NAVY, width=1.4)
    d.pipe([(300, 240), (386, 240)], arrow=False); act = d.valve(400, 240); d.pipe([(414, 240), (520, 240)])
    d.math(535, 240, "q", size=22, anchor="start")
    lt = d.bubble(360, 150, "LT"); d.signal([(300, 150), lt["l"]], arrow=False)
    lc = d.bubble(460, 150, "LC"); d.signal([lt["r"], lc["l"]])
    d.signal([lc["b"], (460, 190), (400, 190), act])
    d.wire([(460, 82), lc["t"]], color=RED); d.math(478, 88, "h^{s}", size=20, color=RED, anchor="start")
    d.math(440, 205, "p", size=19, color=NAVY)
    d.text(160, 286, "load: q_{i}  ·  CV: h  ·  MV: q", size=15, color=GRAY)
    # block diagram
    y = 140
    d.math(620, y - 24, "H^{s}(s)", size=20); s = d.sumj(690, y, {"w": "+", "s": "−"})
    gc = d.box(810, y, "G_{c}", w=96, h=52, kind="red")
    d.wire([(590, y), s["l"]]); d.wire([s["r"], gc["l"]]); d.math(735, y - 22, "E(s)", size=19)
    d.wire([gc["r"], (985, y)]); d.math(930, y - 22, "P(s)", size=19)
    d.wire([(940, 225), (690, 225), s["b"]]); d.math(960, 225, "H(s)", size=19, anchor="middle")
    d.text(800, 262, "measured level fed back", size=14, color=GRAY)
    d.write()


def fb_reduce():
    d = S("fb_reduce", 1000, 250, "Block-diagram algebra: feedback, series and parallel")
    d.text(10, 16, "(a) negative feedback", size=15, color=RED, anchor="start", weight=700)
    y = 90
    d.math(22, y - 22, "R"); s = d.sumj(70, y, {"w": "+", "s": "−"}); g = d.box(185, y, "G", w=80, h=48)
    d.wire([(6, y), s["l"]]); d.wire([s["r"], g["l"]]); d.math(110, y - 20, "E")
    d.wire([g["r"], (310, y)]); d.math(296, y - 22, "Y"); d.dot(270, y)
    h = d.box(185, 170, "H", w=80, h=44)
    d.wire([(270, y), (270, 170), h["r"]]); d.wire([h["l"], (70, 170), s["b"]])
    d.text(350, y, "⇒", size=30, color=NAVY)
    d.wire([(380, y), (412, y)]); d.box(480, y, "G / (1 + GH)", w=136, h=50, kind="soft", size=21); d.wire([(548, y), (585, y)])
    d.text(480, 160, "forward path / (1 + loop)", size=15, color=NAVY, weight=600)
    d.raw(f'<line x1="620" y1="10" x2="620" y2="240" stroke="#ddd" stroke-width="1.5"/>')
    d.text(640, 16, "(b) series", size=15, color=RED, anchor="start", weight=700)
    y = 62
    d.wire([(640, y), (668, y)]); d.box(700, y, "G_{1}", w=62, h=42); d.wire([(731, y), (768, y)])
    d.box(800, y, "G_{2}", w=62, h=42); d.wire([(831, y), (862, y)])
    d.text(880, y, "=", size=24); d.math(940, y, "G_{1}G_{2}", size=22, color=NAVY)
    d.text(640, 122, "(c) parallel", size=15, color=RED, anchor="start", weight=700)
    y1, y2 = 162, 218
    d.wire([(640, 190), (660, 190)], arrow=False); d.dot(660, 190)
    d.wire([(660, 190), (660, y1), (712, y1)]); d.wire([(660, 190), (660, y2), (712, y2)])
    d.box(742, y1, "G_{1}", w=60, h=38); d.box(742, y2, "G_{2}", w=60, h=38)
    sm = d.sumj(820, 190, {"n": "+", "s": "+"})
    d.wire([(772, y1), (820, y1), sm["t"]]); d.wire([(772, y2), (820, y2), sm["b"]]); d.wire([sm["r"], (862, 190)])
    d.text(880, 190, "=", size=24); d.math(940, 190, "G_{1} + G_{2}", size=22, color=NAVY)
    d.write()


def std_loop():
    d = S("std_loop", 1000, 330, "Standard single-loop feedback system, stirred-tank heater")
    y = 160
    d.math(20, y - 26, "R", size=22); d.text(24, y + 26, "T_{sp} [°C]", size=13, color=GRAY)
    km = d.box(95, y, "K_{m}", w=70, h=48)
    s1 = d.sumj(195, y, {"w": "+", "s": "−"}); gc = d.box(285, y, "G_{c}", w=80, h=48, kind="red")
    ga = d.box(430, y, "G_{a}", w=80, h=48); gp = d.box(585, y, "G_{p}", w=80, h=48)
    s3 = d.sumj(700, y, {"w": "+", "n": "+"}); gl = d.box(700, 78, "G_{L}", w=80, h=44)
    gm = d.box(520, 272, "G_{m}", w=80, h=44)
    d.wire([(6, y), km["l"]]); d.wire([km["r"], s1["l"]]); d.text(150, y + 22, "[mA]", size=13, color=GRAY)
    d.wire([s1["r"], gc["l"]]); d.math(228, y - 22, "E", size=20); d.text(240, y + 24, "[mA]", size=13, color=GRAY)
    d.wire([gc["r"], ga["l"]]); d.math(358, y - 22, "P", size=20); d.text(358, y + 22, "[mA]", size=13, color=GRAY)
    d.wire([ga["r"], gp["l"]]); d.math(508, y - 24, "M", size=20); d.text(508, y + 22, "T_{H} [°C]", size=13, color=GRAY)
    d.wire([gp["r"], s3["l"]]); d.wire([s3["r"], (900, y)]); d.math(880, y - 24, "C", size=22)
    d.text(880, y + 22, "T [°C]", size=13, color=GRAY)
    d.wire([(700, 22), gl["t"]]); d.math(718, 28, "L", size=20, anchor="start")
    d.text(752, 28, "T_{i} [°C]", size=13, color=GRAY, anchor="start"); d.wire([gl["b"], s3["t"]])
    d.dot(800, y); d.wire([(800, y), (800, 272), gm["r"]]); d.wire([gm["l"], (195, 272), s1["b"]])
    d.math(330, 252, "C_{m}", size=20); d.text(330, 292, "[mA]", size=13, color=GRAY)
    d.raw(f'<rect x="58" y="110" width="290" height="96" rx="6" fill="none" stroke="{GRAY}" stroke-dasharray="6 4"/>')
    d.text(203, 98, "controller", size=14, color=GRAY)
    d.raw(f'<rect x="530" y="40" width="210" height="166" rx="6" fill="none" stroke="{GRAY}" stroke-dasharray="6 4"/>')
    d.text(635, 222, "process (plant)", size=14, color=GRAY)
    d.text(430, 205, "actuator", size=14, color=GRAY); d.text(520, 312, "sensor + transmitter", size=14, color=GRAY)
    d.write()


def distillation():
    d = S("distillation", 900, 330, "Tray-temperature control of a distillation column")
    d.raw(f'<path d="M300,320 L300,70 Q300,40 340,40 Q380,40 380,70 L380,320" fill="#f7f7fb" stroke="{INK}" stroke-width="2.4"/>')
    d.raw(f'<path d="M298,318 q10,-10 21,0 t21,0 t21,0 t21,0" fill="none" stroke="{INK}" stroke-width="2"/>')
    for k, ch in enumerate("COLUMN"):
        d.text(340, 100 + 26 * k, ch, size=15, color=INK, weight=600)
    d.pipe([(340, 40), (340, 18), (700, 18), (700, 52)])
    d.raw(f'<circle cx="700" cy="72" r="20" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    d.raw(f'<path d="M684,72 l6,-8 l6,16 l6,-16 l6,16 l4,-8" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    d.pipe([(800, 60), (722, 60)]); d.pipe([(722, 84), (800, 84)], arrow=True); d.text(810, 72, "coolant", size=14, anchor="start")
    d.pipe([(700, 92), (700, 116)])
    d.raw(f'<rect x="660" y="118" width="80" height="34" rx="16" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    d.pipe([(700, 152), (700, 186)], arrow=False); d.pipe([(700, 186), (880, 186)]); d.text(820, 168, "distillate", size=15)
    d.pipe([(700, 186), (614, 186)], arrow=False); act = d.valve(600, 186); d.pipe([(586, 186), (380, 186)])
    d.text(470, 168, "reflux", size=15); d.math(520, 168, "R", size=20)
    tt = d.bubble(480, 105, "TT"); d.signal([(380, 105), tt["l"]], arrow=False); d.math(395, 88, "T", size=20)
    tc = d.bubble(600, 105, "TC"); d.signal([tt["r"], tc["l"]]); d.signal([tc["b"], act])
    d.pipe([(160, 250), (300, 250)]); d.text(200, 228, "feed", size=15); d.math(200, 274, "F,  x_{F}", size=19)
    d.write()


def hw_chain():
    d = S("hw_chain", 1000, 312, "Hardware in a temperature loop: signals and their ranges")
    y1, y2 = 90, 230
    c = tbox(d, 120, y1, "controller", sub="PID", kind="red")
    ip = tbox(d, 360, y1, "I/P", sub="current → pressure", w=170)
    v = tbox(d, 600, y1, "control valve", sub="pneumatic", w=170)
    p = tbox(d, 860, 160, "process", sub="stirred tank", w=150, h=200)
    tr = tbox(d, 360, y2, "transmitter", sub="amplifier", w=170)
    sn = tbox(d, 600, y2, "sensor", sub="thermocouple", w=170)
    d.wire([(120, 20), c["t"]], color=RED); d.text(140, 24, "set point", size=14, color=RED, anchor="start")
    d.wire([c["r"], ip["l"]]); d.text(235, y1 - 16, "4–20 mA", size=15, color=NAVY, weight=700)
    d.wire([ip["r"], v["l"]]); d.text(480, y1 - 16, "3–15 psi", size=15, color=NAVY, weight=700)
    d.wire([v["r"], (785, y1)]); d.text(735, y1 - 16, "steam q", size=14)
    d.wire([(785, y2), sn["r"]]); d.text(735, y2 - 16, "T (°C)", size=14)
    d.wire([sn["l"], tr["r"]]); d.text(480, y2 - 16, "mV", size=15, color=NAVY, weight=700)
    d.wire([tr["l"], (120, y2), c["b"]]); d.text(220, y2 - 16, "4–20 mA", size=15, color=NAVY, weight=700)
    d.raw(f'<rect x="262" y="40" width="436" height="88" rx="8" fill="none" stroke="{GRAY}" stroke-dasharray="6 4"/>')
    d.raw(f'<rect x="262" y="194" width="436" height="88" rx="8" fill="none" stroke="{GRAY}" stroke-dasharray="6 4"/>')
    d.math(480, 150, "G_{a}", size=20, color=GRAY); d.text(520, 150, "actuator", size=13, color=GRAY, anchor="start")
    d.math(480, 298, "G_{m}", size=20, color=GRAY); d.text(520, 298, "transducer", size=13, color=GRAY, anchor="start")
    d.write()


# --------------------------------------------------------------------------- 2.2-2.3
def unity():
    d = S("unity", 640, 170, "Unity-feedback servo loop")
    y = 70
    d.math(20, y - 24, "R"); s = d.sumj(70, y, {"w": "+", "s": "−"})
    gc = d.box(200, y, "G_{c}", w=96, h=52, kind="red"); gp = d.box(360, y, "G_{p}", w=96, h=52)
    d.wire([(6, y), s["l"]]); d.wire([s["r"], gc["l"]]); d.math(115, y - 22, "E")
    d.wire([gc["r"], gp["l"]]); d.wire([gp["r"], (520, y)]); d.math(505, y - 24, "C"); d.dot(470, y)
    d.wire([(470, y), (470, 145), (70, 145), s["b"]])
    d.text(270, 160, "G_{m} = G_{a} = 1,  L = 0", size=14, color=GRAY)
    d.write()


def deriv_meas():
    d = S("deriv_meas", 580, 230, "PI on the error, derivative on the measurement")
    y = 70
    d.math(20, y - 24, "R"); s = d.sumj(80, y, {"w": "+", "s": "−"})
    pi = d.box(300, y, "K_{c}(1 + 1/τ_{I}s)", w=200, h=54, kind="red", size=22)
    d.wire([(6, y), s["l"]]); d.wire([s["r"], pi["l"]]); d.math(140, y - 22, "E")
    d.wire([pi["r"], (520, y)]); d.math(505, y - 24, "P")
    dd = d.box(300, 170, "(τ_{D}s + 1)/(ατ_{D}s + 1)", w=250, h=54, kind="soft", size=21)
    d.wire([(520, 170), dd["r"]]); d.math(540, 170, "C", anchor="start")
    d.wire([dd["l"], (80, 170), s["b"]])
    d.text(300, 214, "derivative action on the measured variable", size=14, color=NAVY)
    d.write()


def problem2():
    d = S("problem2", 1000, 290, "Stirred-tank heater under P control, block diagram with units")
    y = 140
    d.math(22, y - 26, "T'_{sp}", size=19); d.text(22, y + 22, "[°F]", size=13, color=GRAY)
    km = d.box(95, y, "K_{m}", w=64, h=46)
    s = d.sumj(190, y, {"w": "+", "s": "−"}); kc = d.box(275, y, "K_{c}", w=64, h=46, kind="red")
    kip = d.box(395, y, "K_{IP}", w=70, h=46); kv = d.box(515, y, "K_{v}", w=64, h=46)
    k2 = d.box(660, y, "K_{2}/(τs+1)", w=128, h=48, size=20)
    s2 = d.sumj(790, y, {"w": "+", "n": "+"}); k1 = d.box(660, 50, "K_{1}/(τs+1)", w=128, h=44, size=20)
    d.wire([(4, y), km["l"]]); d.wire([km["r"], s["l"]]); d.math(146, y - 30, "T̃'_{sp}", size=17); d.text(150, y + 22, "[mA]", size=13, color=GRAY)
    d.wire([s["r"], kc["l"]]); d.math(225, y - 22, "E", size=18); d.text(236, y + 24, "[mA]", size=13, color=GRAY)
    d.wire([kc["r"], kip["l"]]); d.math(335, y - 22, "P'", size=18); d.text(335, y + 22, "[mA]", size=13, color=GRAY)
    d.wire([kip["r"], kv["l"]]); d.math(455, y - 22, "P'_{t}", size=18); d.text(455, y + 22, "[psi]", size=13, color=GRAY)
    d.wire([kv["r"], k2["l"]]); d.math(570, y - 22, "P'_{s}", size=18); d.text(570, y + 22, "[psi]", size=13, color=GRAY)
    d.wire([k2["r"], s2["l"]]); d.wire([s2["r"], (975, y)]); d.math(950, y - 24, "T'", size=19); d.text(950, y + 22, "[°F]", size=13, color=GRAY)
    d.wire([(520, 50), k1["l"]]); d.math(500, 50, "T'_{i}", size=18, anchor="end")
    d.wire([k1["r"], (790, 50), s2["t"]])
    km2 = d.box(560, 240, "K_{m}", w=64, h=44)
    d.dot(890, y); d.wire([(890, y), (890, 240), km2["r"]]); d.wire([km2["l"], (190, 240), s["b"]])
    d.math(400, 222, "T'_{m}", size=18); d.text(400, 262, "[mA]", size=13, color=GRAY)
    d.write()


def blending():
    d = S("blending3", 900, 340, "Liquid blending system with composition control")
    tank(d, 200, 440, 120, 312, 170)
    d.raw(f'<rect x="296" y="62" width="48" height="34" rx="4" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    d.raw(f'<line x1="320" y1="96" x2="320" y2="270" stroke="{INK}" stroke-width="2"/>')
    d.raw(f'<rect x="292" y="262" width="56" height="12" rx="3" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    d.pipe([(20, 100), (250, 100), (250, 160)]); d.math(40, 78, "q_{1}, c_{1}", size=19, anchor="start")
    d.pipe([(880, 100), (714, 100)], arrow=False); act = d.valve(700, 100)
    d.pipe([(686, 100), (400, 100), (400, 160)]); d.math(860, 78, "q_{2}, c_{2}", size=19, anchor="end")
    d.pipe([(440, 290), (546, 290)], arrow=False); bowtie(d, 560, 290); d.pipe([(574, 290), (880, 290)])
    d.math(860, 312, "q_{3}, c_{3}", size=19, anchor="end")
    d.math(222, 240, "h", size=22, color=NAVY)
    at = d.bubble(520, 225, "AT"); d.signal([(440, 225), at["l"]], arrow=False)
    ac = d.bubble(520, 155, "AC"); d.signal([at["t"], ac["b"]])
    ip = d.bubble(620, 155, "I/P"); d.signal([ac["r"], ip["l"]])
    d.signal([ip["t"], (620, 40), (700, 40), act])
    d.text(580, 196, "2-min measurement delay", size=13, color=GRAY, anchor="start")
    d.write()


if __name__ == "__main__":
    for f in (level_loop, fb_reduce, std_loop, distillation, hw_chain, unity, deriv_meas, problem2, blending):
        f()
    print(sorted(p.name for p in HERE.glob("_*.md")))
