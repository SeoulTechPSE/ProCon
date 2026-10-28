"""Inline-SVG diagrams for Ch.1 (uses the shared helper tools/svgdiagram.py).
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


def tank(d, x0, x1, y0, y1, ylev, label=None):
    d.raw(f'<rect x="{x0 + 2}" y="{ylev}" width="{x1 - x0 - 4}" height="{y1 - ylev - 2}" fill="{LIQ}"/>')
    waves = " ".join(f"Q{x + 8},{ylev - 5} {x + 16},{ylev}" for x in range(x0 + 4, x1 - 16, 16))
    d.raw(f'<path d="M{x0 + 4},{ylev} {waves}" fill="none" stroke="{NAVY}" stroke-width="1.2"/>')
    d.raw(f'<path d="M{x0},{y0} L{x0},{y1} L{x1},{y1} L{x1},{y0}" fill="none" stroke="{INK}" stroke-width="2.6"/>')
    if label:
        d.text((x0 + x1) / 2, y1 + 18, label, size=14, color=GRAY)


def mixer(d, cx, ytop, ybot):
    d.raw(f'<rect x="{cx - 20}" y="{ytop - 30}" width="40" height="24" rx="4" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    d.raw(f'<line x1="{cx}" y1="{ytop - 6}" x2="{cx}" y2="{ybot}" stroke="{INK}" stroke-width="2"/>')
    d.raw(f'<rect x="{cx - 24}" y="{ybot - 6}" width="48" height="12" rx="3" fill="#fff" stroke="{INK}" stroke-width="2"/>')


def coil(d, x0, x1, y):
    n = int((x1 - x0) / 14)
    p = " ".join(f"a7,9 0 1 1 14,0" for _ in range(n))
    d.raw(f'<path d="M{x0},{y} {p}" fill="none" stroke="{RED}" stroke-width="2"/>')


def bowtie(d, cx, cy, s=11):
    d.raw(f'<path d="M{cx - s},{cy - s * 0.8} L{cx + s},{cy + s * 0.8} L{cx + s},{cy - s * 0.8} '
          f'L{cx - s},{cy + s * 0.8} Z" fill="#fff" stroke="{INK}" stroke-width="2"/>')


def height(d, x, ytop, ybot, lab):
    d.wire([(x, (ytop + ybot) / 2), (x, ytop + 2)], color=NAVY, width=1.4)
    d.wire([(x, (ytop + ybot) / 2), (x, ybot - 2)], color=NAVY, width=1.4)
    d.math(x + 14, (ytop + ybot) / 2, lab, size=22, color=NAVY, anchor="start")


# --------------------------------------------------------------------------- models
def mixing_tank():
    d = S("mixing_tank", 560, 272, "Well-mixed tank with inlet and outlet concentration")
    tank(d, 150, 390, 60, 240, 100)
    mixer(d, 270, 60, 200)
    d.pipe([(20, 40), (190, 40), (190, 92)]); d.math(40, 18, "q,  c_{in}(t)", size=20, anchor="start")
    d.pipe([(390, 220), (540, 220)]); d.math(540, 196, "q,  c(t)", size=20, anchor="end")
    d.math(320, 160, "V", size=22, color=NAVY)
    d.text(270, 254, "space time  τ = V/q", size=15, color=GRAY)
    d.write()


def level_tank():
    d = S("level_tank", 520, 280, "Liquid tank with square-root outflow")
    tank(d, 130, 370, 50, 250, 100)
    d.pipe([(20, 30), (180, 30), (180, 92)]); d.math(40, 14, "q_{i}", size=22)
    height(d, 330, 100, 250, "h")
    d.pipe([(370, 230), (500, 230)]); d.math(490, 206, "q = β√h", size=20, anchor="end")
    d.text(250, 270, "cross-sectional area A", size=15, color=GRAY)
    d.write()


def heater():
    d = S("heater", 560, 290, "Stirred-tank heater")
    tank(d, 150, 400, 60, 250, 100)
    mixer(d, 275, 60, 165)
    coil(d, 190, 360, 215)
    d.pipe([(20, 40), (200, 40), (200, 92)]); d.math(40, 18, "T_{i},  q", size=20, anchor="start")
    d.pipe([(400, 110), (550, 110)]); d.math(550, 88, "T,  q", size=20, anchor="end")
    d.math(330, 140, "V,  ρ", size=20, color=NAVY)
    d.math(275, 272, "UA(T_{H} − T)", size=19, color=RED)
    d.write()


def cstr():
    d = S("cstr", 600, 320, "Non-isothermal CSTR with cooling coil")
    tank(d, 170, 430, 60, 260, 100)
    mixer(d, 300, 60, 170)
    coil(d, 205, 395, 222)
    d.pipe([(20, 40), (220, 40), (220, 92)]); d.text(40, 16, "pure A", size=15, anchor="start")
    d.math(120, 62, "q, c_{Ai}, T_{i}", size=19)
    d.pipe([(430, 110), (590, 110)]); d.math(590, 88, "q, c_{A}, T", size=19, anchor="end")
    d.math(360, 145, "V, ρ, T", size=19, color=NAVY)
    d.pipe([(205, 300), (205, 228)]); d.pipe([(395, 228), (395, 300)])
    d.math(300, 300, "coolant  T_{c}", size=19, color=RED)
    d.text(520, 170, "A → B", size=15, color=GRAY)
    d.math(520, 196, "r = k_{0}e^{−E/RT} c_{A}", size=17, color=GRAY)
    d.write()


def two_tanks():
    d = S("two_tanks", 700, 292, "Two stirred tanks in series")
    tank(d, 90, 290, 60, 230, 95, "stage 1:  V_{1} = 4 m³")
    mixer(d, 190, 60, 195)
    tank(d, 400, 600, 110, 260, 145, "")
    d.text(500, 274, "stage 2:  V_{2} = 3 m³", size=14, color=GRAY)
    mixer(d, 500, 110, 228)
    d.pipe([(10, 40), (130, 40), (130, 88)]); d.math(30, 20, "c_{i}(t)", size=20)
    d.pipe([(290, 90), (440, 90), (440, 138)]); d.math(360, 70, "c_{1}", size=20)
    d.pipe([(600, 140), (690, 140)]); d.math(670, 118, "c_{2}", size=20)
    d.text(345, 22, "q = 2 m³/min,  nominal c_{i} = 1 kmol/m³", size=15, color=NAVY)
    d.write()


def storage():
    d = S("storage", 640, 262, "Storage tank with pumped inlet and outlet: an integrating process")
    tank(d, 220, 420, 40, 220, 110)
    height(d, 390, 110, 220, "h")
    for cx in (130, 510):
        d.raw(f'<circle cx="{cx}" cy="200" r="17" fill="#fff" stroke="{INK}" stroke-width="2"/>')
        d.raw(f'<path d="M{cx - 8},{193} L{cx + 10},{200} L{cx - 8},{207} Z" fill="{INK}"/>')
    d.pipe([(20, 200), (113, 200)], arrow=False); d.pipe([(147, 200), (190, 200), (190, 60), (250, 60), (250, 102)])
    d.math(150, 168, "q_{in}", size=20)
    d.pipe([(420, 200), (493, 200)], arrow=False); d.pipe([(527, 200), (630, 200)]); d.math(575, 178, "q", size=20)
    d.text(130, 232, "transfer pump", size=13, color=GRAY); d.text(510, 232, "feed pump", size=13, color=GRAY)
    d.text(320, 244, "outflow set by the pump, not by h", size=14, color=RED)
    d.write()


def dead_time_pipe():
    d = S("dead_time_pipe", 720, 150, "Plug flow in a pipe produces a pure time delay")
    d.raw(f'<line x1="80" y1="40" x2="560" y2="40" stroke="{INK}" stroke-width="2.4"/>')
    d.raw(f'<line x1="80" y1="110" x2="560" y2="110" stroke="{INK}" stroke-width="2.4"/>')
    for x in (110, 300, 500):
        for y in (55, 75, 95):
            d.wire([(x, y), (x + 36, y)], color=NAVY, width=1.6)
    d.math(60, 75, "x(t)", size=20, anchor="end"); d.math(580, 75, "y(t) = x(t − θ)", size=20, anchor="start")
    d.text(320, 134, "flat velocity profile:  θ = L/v = V_{pipe}/q", size=15, color=GRAY)
    d.write()


def noninteracting():
    d = S("noninteracting", 640, 410, "Non-interacting tanks in series")
    xs = [(40, 200, 40, 150), (230, 390, 170, 280), (420, 580, 290, 390)]
    for i, (x0, x1, y0, y1) in enumerate(xs):
        tank(d, x0, x1, y0, y1, y0 + 30)
        height(d, x0 + 110, y0 + 30, y1, f"h_{{{i + 1}}}")
        bowtie(d, x1 + 20, y1 - 12); d.pipe([(x1, y1 - 12), (x1 + 9, y1 - 12)], arrow=False)
        if i < 2:
            d.pipe([(x1 + 31, y1 - 12), (x1 + 60, y1 - 12), (x1 + 60, xs[i + 1][2] + 22)])
        else:
            d.pipe([(x1 + 31, y1 - 12), (x1 + 58, y1 - 12)])
        d.math(x1 + 22, y1 - 34, f"R_{{{i + 1}}}", size=17, color=GRAY)
    d.pipe([(10, 20), (80, 20), (80, 64)]); d.math(30, 6, "q_{i}", size=19)
    d.text(150, 300, "q_{i} = h_{i}/R_{i}  (linear resistance)", size=15, color=NAVY)
    d.write()


def interacting():
    d = S("interacting", 640, 230, "Two interacting tanks")
    tank(d, 60, 260, 40, 190, 70); tank(d, 340, 540, 40, 190, 90)
    height(d, 220, 70, 190, "h_{1}"); height(d, 500, 90, 190, "h_{2}")
    d.pipe([(260, 175), (289, 175)], arrow=False); bowtie(d, 300, 175); d.pipe([(311, 175), (340, 175)])
    d.math(300, 150, "R_{1}", size=18, color=GRAY); d.math(300, 205, "q_{1} = (h_{1} − h_{2})/R_{1}", size=17, color=RED)
    d.pipe([(540, 175), (569, 175)], arrow=False); bowtie(d, 580, 175); d.pipe([(591, 175), (630, 175)])
    d.math(580, 150, "R_{2}", size=18, color=GRAY); d.math(610, 200, "q_{2}", size=18)
    d.pipe([(10, 20), (110, 20), (110, 62)]); d.math(30, 6, "q_{i}", size=19)
    d.write()


def parallel():
    d = S("parallel", 560, 200, "Two first-order elements in parallel")
    d.math(30, 78, "X(s)", size=20); d.wire([(10, 100), (90, 100)], arrow=False); d.dot(90, 100)
    d.wire([(90, 100), (90, 45), (215, 45)]); d.wire([(90, 100), (90, 155), (215, 155)])
    d.box(270, 45, "K_{1}/(τ_{1}s + 1)", w=150, h=46, size=20)
    d.box(270, 155, "K_{2}/(τ_{2}s + 1)", w=150, h=46, size=20)
    sm = d.sumj(430, 100, {"n": "+", "s": "+"})
    d.wire([(345, 45), (430, 45), sm["t"]]); d.wire([(345, 155), (430, 155), sm["b"]]); d.wire([sm["r"], (540, 100)])
    d.math(520, 78, "Y(s)", size=20)
    d.write()


def manometer():
    d = S("manometer", 460, 372, "U-tube manometer set in motion by a pressure step")
    xl0, xl1, xr0, xr1, yb = 120, 160, 300, 340, 300
    d.raw(f'<path d="M{xl0},{40} L{xl0},{yb - 60} A{(xr1 - xl0) / 2},{90} 0 0 0 {xr1},{yb - 60} L{xr1},{40}" '
          f'fill="none" stroke="{INK}" stroke-width="2.4"/>')
    d.raw(f'<path d="M{xl1},{40} L{xl1},{yb - 60} A{(xr0 - xl1) / 2},{50} 0 0 0 {xr0},{yb - 60} L{xr0},{40}" '
          f'fill="none" stroke="{INK}" stroke-width="2.4"/>')
    d.raw(f'<path d="M{xl0 + 1},{170} L{xl0 + 1},{yb - 60} A{(xr1 - xl0) / 2 - 1},{89} 0 0 0 {xr1 - 1},{yb - 60} '
          f'L{xr1 - 1},{110} L{xr0 + 1},{110} L{xr0 + 1},{yb - 60} A{(xr0 - xl1) / 2 + 1},{51} 0 0 1 {xl1 - 1},{yb - 60} '
          f'L{xl1 - 1},{170} Z" fill="{LIQ}" stroke="none"/>')
    d.wire([(140, 8), (140, 36)], color=RED); d.math(160, 14, "p_{a}", size=20, color=RED, anchor="start")
    d.wire([(320, 8), (320, 36)], color=RED); d.math(340, 14, "p_{b}", size=20, color=RED, anchor="start")
    d.raw(f'<line x1="90" y1="140" x2="370" y2="140" stroke="{GRAY}" stroke-dasharray="5 4"/>')
    d.text(380, 140, "rest level", size=13, color=GRAY, anchor="start")
    d.wire([(360, 140), (360, 112)], color=NAVY, width=1.4); d.math(372, 122, "h(t)", size=18, color=NAVY, anchor="start")
    d.wire([(100, 140), (100, 168)], color=NAVY, width=1.4); d.math(88, 156, "h(t)", size=18, color=NAVY, anchor="end")
    d.text(230, 352, "liquid column length L, tube radius R", size=14, color=GRAY)
    d.write()


if __name__ == "__main__":
    for f in (mixing_tank, level_tank, heater, cstr, two_tanks, storage, dead_time_pipe,
              noninteracting, interacting, parallel, manometer):
        f()
    print(sorted(p.name for p in HERE.glob("_*.md")))
