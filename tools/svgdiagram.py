"""Shared inline-SVG helper for slide diagrams (block diagrams, simplified P&IDs).

    from svgdiagram import SVG, NAVY, RED
    d = SVG("name", 980, 300, "aria label", out=Path("diagrams")); ...; d.write()

Writes diagrams/_<name>.md as a Quarto ```{=html}``` include.
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
    def __init__(self, name, w, h, label, out=None):
        self.name, self.w, self.h, self.label, self.el = name, w, h, label, []
        self.out = Path(out) if out else OUT
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
        (self.out / f"_{self.name}.md").write_text("```{=html}\n" + svg + "\n```\n")
        return svg


