"""Inline-SVG diagrams for Ch.3 (uses the shared helper tools/svgdiagram.py).
    python diagrams/make_diagrams.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from svgdiagram import SVG, NAVY, RED, GREEN, GRAY, INK  # noqa: E402


def S(name, w, h, label):
    return SVG(name, w, h, label, out=HERE)


def prc_test():
    d = S("prc_test", 980, 312, "Open-loop step test: the process-reaction curve")
    y = 150
    d.math(20, y - 22, "R"); km = d.box(80, y, "K_{m}", w=70, h=48)
    s1 = d.sumj(205, y, {"w": "+", "s": "−"}); gc = d.box(290, y, "G_{c}", w=86, h=48, kind="ghost")
    ga = d.box(470, y, "G_{a}", w=80, h=48); gp = d.box(610, y, "G_{p}", w=80, h=48)
    s3 = d.sumj(740, y, {"w": "+", "n": "+"}); gl = d.box(740, 70, "G_{L}", w=80, h=44)
    gm = d.box(560, 255, "G_{m}", w=80, h=44)
    d.wire([(6, y), km["l"]]); d.wire([km["r"], s1["l"]]); d.math(152, y - 24, "R_{m}")
    d.wire([s1["r"], gc["l"]], dash=True, color="#bbb"); d.wire([gc["r"], (380, y)], arrow=False, dash=True, color="#bbb")
    d.text(290, y + 44, "loop opened", size=14, color=GRAY)
    d.wire([(400, 70), (400, y), ga["l"]]); d.text(400, 40, "step input", size=15, color=RED)
    d.math(400, 58, "P = M/s", size=18, color=RED)
    d.wire([ga["r"], gp["l"]]); d.wire([gp["r"], s3["l"]]); d.wire([s3["r"], (960, y)]); d.math(945, y - 22, "C")
    d.wire([(740, 18), gl["t"]]); d.math(758, 24, "L = 0", anchor="start", size=18); d.wire([gl["b"], s3["t"]])
    d.raw(f'<rect x="{430}" y="{38}" width="{370}" height="{150}" rx="6" fill="none" stroke="{GRAY}" stroke-dasharray="6 4"/>')
    d.text(790, 176, "process", size=14, color=GRAY)
    d.dot(870, y); d.wire([(870, y), (870, 255), gm["r"]]); d.wire([gm["l"], (330, 255)])
    d.text(260, 256, "record C_{m}", size=15, color=RED)
    d.text(560, 296, "G_{PRC} = C_{m}/P = G_{a}G_{p}G_{m}", size=16, color=NAVY)
    d.write()


def imc():
    d = S("imc", 1000, 400, "Internal model control and the equivalent conventional loop")
    d.text(20, 18, "(a) IMC structure", size=16, color=RED, anchor="start", weight=700)
    y = 150
    d.math(20, y - 22, "R"); s1 = d.sumj(70, y, {"w": "+", "s": "−"})
    q = d.box(190, y, "G_{c}^{*}", w=90, h=50, kind="red"); gp = d.box(400, y, "G_{p}", w=90, h=50)
    s3 = d.sumj(530, y, {"w": "+", "n": "+"}); gl = d.box(530, 66, "G_{L}", w=80, h=44)
    mdl = d.box(400, 245, "G̃_{p}", w=90, h=50, kind="soft"); s4 = d.sumj(590, 245, {"n": "+", "w": "−"})
    d.wire([(6, y), s1["l"]]); d.wire([s1["r"], q["l"]]); d.math(110, y - 20, "E")
    d.wire([q["r"], gp["l"]]); d.math(275, y - 20, "P"); d.wire([gp["r"], s3["l"]]); d.wire([s3["r"], (680, y)])
    d.math(668, y - 22, "C"); d.wire([(530, 14), gl["t"]]); d.math(548, 20, "L", anchor="start"); d.wire([gl["b"], s3["t"]])
    d.dot(290, y); d.wire([(290, y), (290, 245), mdl["l"]]); d.wire([mdl["r"], s4["l"]]); d.math(480, 225, "C̃")
    d.dot(620, y); d.wire([(620, y), s4["t"]]) if False else d.wire([(620, y), (620, 200), (590, 200), s4["t"]])
    d.wire([s4["b"], (590, 320), (70, 320), s1["b"]]); d.math(330, 340, "C − C̃", size=20)
    d.text(400, 290, "internal model", size=14, color=NAVY)
    d.text(330, 365, "only the model error is fed back", size=14, color=GREEN)
    # (b)
    ox = 700
    d.text(ox, 18, "(b) equivalent loop", size=16, color=RED, anchor="start", weight=700)
    y = 150
    s = d.sumj(ox + 30, y, {"w": "+", "s": "−"}); gc = d.box(ox + 120, y, "G_{c}", w=76, h=46); g = d.box(ox + 225, y, "G_{p}", w=76, h=46)
    d.wire([(ox - 10, y), s["l"]]); d.wire([s["r"], gc["l"]]); d.wire([gc["r"], g["l"]]); d.wire([g["r"], (ox + 292, y)])
    d.dot(ox + 270, y); d.wire([(ox + 270, y), (ox + 270, 210), (ox + 30, 210), s["b"]])
    d.math(ox + 145, 270, "G_{c} = G_{c}^{*} / (1 − G_{c}^{*}G̃_{p})", size=20, color=NAVY)
    d.write()


def heat_exchanger():
    d = S("heat_exchanger", 900, 330, "Steam-heated shell-and-tube exchanger with temperature control")
    hx, hy, hw, hh = 300, 150, 300, 80
    d.raw(f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="6" fill="#f7f7fb" stroke="{INK}" stroke-width="2.4"/>')
    for k in range(3):
        d.raw(f'<line x1="{hx + 12 + 8 * k}" y1="{hy}" x2="{hx + 12 + 8 * k}" y2="{hy + hh}" stroke="{INK}" stroke-width="1.6"/>')
    d.text(hx + hw / 2, hy + hh / 2, "heat exchanger", size=17)
    d.pipe([(860, hy + hh / 2), (hx + hw, hy + hh / 2)]); d.math(870, hy + hh / 2, "T_{1}", anchor="start")
    d.pipe([(hx, hy + hh / 2), (40, hy + hh / 2)]); d.math(26, hy + hh / 2, "T_{2}", anchor="end")
    d.pipe([(860, 100), (574, 100)], arrow=False); act = d.valve(560, 100)
    d.pipe([(546, 100), (420, 100), (420, hy)]); d.text(800, 82, "steam", size=16); d.math(500, 120, "P_{s}", size=18)
    d.pipe([(520, hy + hh), (520, 300), (640, 300)]); d.text(700, 300, "condensate (trap)", size=15)
    tt = d.bubble(160, 110, "TT"); d.signal([(160, hy + hh / 2), tt["b"]], arrow=False)
    tc = d.bubble(160, 40, "TC"); d.signal([tt["t"], tc["b"]])
    ip = d.bubble(320, 40, "I/P"); d.signal([tc["r"], ip["l"]]); d.signal([ip["r"], (560, 40), act])
    d.math(132, 76, "T_{2m}", size=16, anchor="end")
    d.write()


if __name__ == "__main__":
    for f in (prc_test, imc, heat_exchanger):
        f()
    print(sorted(p.name for p in HERE.glob("_*.md")))
