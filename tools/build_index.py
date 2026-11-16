"""Generate the site's index pieces from tools/chapters.py (run automatically as Quarto pre-render).

    python3 tools/build_index.py

Writes
    _chapters.md   chapter cards for index.qmd (topics, thumbnail, links, widgets, PDF sizes, last update)
    _roadmap.md    course map (inline SVG) for index.qmd
    _updates.md    announcements (UPDATES in tools/chapters.py) for index.qmd
    contents.qmd   every slide title of every deck, linked (searchable: reveal decks are not indexed)
    problems.qmd   homework problems of all chapters, linked to their slides
    matlab.qmd     every MATLAB code tab, by chapter, + chN/matlab/*.m and chN/matlab/chN_matlab.zip
    README.md      chapter table between <!-- chapters:start --> and <!-- chapters:end -->
Only the standard library is required (Pillow is used for thumbnails when available).
"""
import html
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from chapters import CHAPTERS, SITE, REPO, UPDATES  # noqa: E402

COLAB = f"https://colab.research.google.com/github/{REPO}/blob/main"


# ------------------------------------------------------------------ helpers
def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return ""


def size(path):
    p = ROOT / path
    return f"{p.stat().st_size / 1e6:.1f} MB" if p.exists() else ""


def clean_title(t):
    t = re.sub(r"\[(NEW|FIX)\]\{\.(new|fix)\}", "", t)
    t = re.sub(r"\[([^\]]*)\]\{[^}]*\}", r"\1", t)           # [Example 1.1]{.ex} -> Example 1.1
    t = t.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", t).strip()


POS = {}                                                        # (qmd, flat index) -> reveal hash "h" or "h/v"


def slides(qmd):
    """[(flat index, level, title, body_lines)]; flat index = slide number - 1 (title slide = 0).

    Level-1 headings open a vertical stack in reveal.js, so the URL of a slide is #/h/v,
    not the flat number; hash(qmd, k) gives it.
    """
    out, fence, k, h, v, stack = [], False, 0, 0, 0, False
    for line in (ROOT / qmd).read_text(encoding="utf-8").split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and re.match(r"^#{1,2} ", line):
            k += 1
            lev = len(line.split(" ")[0])
            if lev == 1:
                h, v, stack = h + 1, 0, True
            elif stack:
                v += 1
            else:
                h, v = h + 1, 0
            POS[(qmd, k)] = f"{h}/{v}" if v else f"{h}"
            out.append([k, lev, clean_title(line.split(" ", 1)[1]), []])
        elif out:
            out[-1][3].append(line)
    return out


def hash_(qmd, k):
    return POS[(qmd, k)]


def summary(body, limit=230):
    """First prose sentence(s) of a slide body, safe to cut (keeps $...$ balanced)."""
    text, inmath, fence, disp = [], False, False, []
    for ln in body:
        s = ln.strip()
        if s.startswith("```"):
            fence = not fence; continue
        if fence:
            continue
        if s == "$$":
            if inmath:                                          # short display math -> inline
                m = " ".join(disp).strip()
                if len(m) < 90 and "\\\\" not in m:
                    text.append(f"${m}$")
            inmath, disp = not inmath, []
            continue
        if inmath:
            disp.append(s); continue
        if not s or s[0] in ":{|!<" or s.startswith("{{"):
            continue
        text.append(s)
        if len(" ".join(text)) > limit:
            break
    parts = " ".join(text).split("$")                         # strip markdown emphasis/escapes outside math
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"\\([()])", r"\1", parts[i].replace("*", ""))
    t = re.sub(r"\s+", " ", "$".join(parts))
    if len(t) > limit:
        cut = t[:limit].rsplit(" ", 1)[0]
        if cut.count("$") % 2:
            cut = cut[:cut.rfind("$")].rstrip()
        t = cut.rstrip(",;:") + " …"
    return t


def thumbnail(ch):
    src, dst = ROOT / ch["thumb"], ROOT / "assets" / "thumbs" / f"ch{ch['n']}.png"
    try:
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            from PIL import Image
            dst.parent.mkdir(parents=True, exist_ok=True)
            im = Image.open(src).convert("RGB"); w, h = im.size
            tw, th = 640, 360                                   # fit the whole figure into 16:9, white margins
            scale = min((tw - 16) / w, (th - 12) / h); im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
            canvas = Image.new("RGB", (tw, th), "white"); canvas.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
            canvas.save(dst, optimize=True)
        return f"assets/thumbs/ch{ch['n']}.png"
    except Exception:                                           # no Pillow (e.g. CI): use the committed thumbnail
        return f"assets/thumbs/ch{ch['n']}.png" if dst.exists() else ch["thumb"]


# ------------------------------------------------------------------ pieces
def cards():
    out = ['```{=html}', '<div class="chapter-grid">']
    for ch in CHAPTERS:
        n, s, d = ch["n"], ch["slug"], f"ch{ch['n']}"
        upd = git("log", "-1", "--format=%cs", "--", d)
        pdf, ho = f"{d}/{s}.pdf", f"{d}/{s}_handout.pdf"
        topics = " · ".join(html.escape(t) for t in ch["topics"])
        widgets = " ".join(f'<a class="chip" href="{w}">▶ {html.escape(nm)}</a>' for nm, w in ch["widgets"])
        out.append(f'''<article class="chapter-card">
  <a class="thumb" href="{d}/{s}.html"><img src="{thumbnail(ch)}" alt="Chapter {n} figure" loading="lazy"></a>
  <div class="card-body">
    <div class="card-num">Chapter {n}{f'<span class="updated">updated {upd}</span>' if upd else ''}</div>
    <h3><a href="{d}/{s}.html">{html.escape(ch["title"])}</a></h3>
    <p class="topics">{topics}</p>
    <div class="links">
      <a class="btn primary" href="{d}/{s}.html">Slides</a>
      <a class="btn" href="{pdf}">PDF <small>{size(pdf)}</small></a>
      <a class="btn" href="{ho}">Handout <small>{size(ho)}</small></a>
      <a class="btn" href="{COLAB}/{d}/{s}.ipynb">Colab</a>
    </div>
    <div class="widgets">{widgets}</div>
  </div>
</article>''')
    out += ['</div>', '```', '']
    return "\n".join(out)


# ------------------------------------------------------------------ course map
ROADMAP = {   # chapter -> (centre x, centre y, short title, two topic lines)
    1: (130, 205, "Dynamic Response", ["Laplace, transfer functions", "1st/2nd order, dead time"]),
    2: (410, 205, "Single-Loop Analysis", ["closed loop, block diagrams", "P / PI / PID modes"]),
    3: (690, 95, "Tuning", ["ZN, Cohen–Coon, ITAE", "direct synthesis, IMC"]),
    4: (690, 315, "Stability", ["Routh–Hurwitz", "root locus"]),
    5: (960, 315, "Frequency Response", ["Bode, Nyquist", "gain & phase margins"]),
    6: (960, 95, "Multi-loop Systems", ["cascade, feedforward, Smith", "ratio, RGA, decoupling"]),
}
EDGES = [(1, 2, ""), (2, 3, ""), (2, 4, ""), (4, 5, ""), (3, 6, ""), (5, 6, "")]
DASHED = [(4, 3, ['K<tspan dy="4" font-size="11">cu</tspan><tspan dy="-4">, T</tspan><tspan dy="4" font-size="11">u</tspan>',
                  "→ ZN tuning"]),
          (5, 3, ["tune by", "GM, PM"]),
          (1, 3, ["FOPDT model"])]


def roadmap():
    W, H, bw, bh = 1100, 430, 228, 112
    NAVY, RED, GREEN, GRAY = "#333399", "#C00000", "#2E7D32", "#888"
    by = {c["n"]: c for c in CHAPTERS}
    box = lambda n: ROADMAP[n][:2]
    out = [f'<svg class="roadmap" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-label="Course map: how the six chapters build on each other">',
           '<defs><marker id="rm-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker>'
           f'<filter id="rm-sh" x="-10%" y="-10%" width="130%" height="140%"><feDropShadow dx="0" dy="2" '
           f'stdDeviation="3" flood-color="{NAVY}" flood-opacity="0.15"/></filter></defs>']
    # stage bands
    for x0, x1, lab in [(10, 262, "Foundations"), (282, 538, "Closed loop"), (558, 1090, "Design & analysis")]:
        out.append(f'<rect x="{x0}" y="10" width="{x1 - x0}" height="{H - 20}" rx="12" fill="#f7f8fc"/>')
        out.append(f'<text x="{(x0 + x1) / 2}" y="{H - 22}" text-anchor="middle" font-size="15" '
                   f'font-weight="700" fill="{GRAY}" letter-spacing=".08em">{lab.upper()}</text>')

    def edge(a, b, dashed=False, label=""):
        (xa, ya), (xb, yb) = box(a), box(b)
        if ya == yb:                                    # horizontal
            sx = 1 if xb > xa else -1
            p = f"M{xa + sx * bw / 2},{ya} L{xb - sx * bw / 2},{yb}"; lx, ly = (xa + xb) / 2, ya - 10
        elif xa == xb:                                  # vertical
            sy = 1 if yb > ya else -1
            p = f"M{xa},{ya + sy * bh / 2} L{xb},{yb - sy * bh / 2}"; lx, ly = xa - 12, (ya + yb) / 2 - 6
        else:                                           # elbow: out of the side, into top/bottom or side
            sx = 1 if xb > xa else -1
            if a == 1:                                   # long dashed route above everything
                p = f"M{xa},{ya - bh / 2} L{xa},{40} L{xb - bw / 2 - 30},{40} L{xb - bw / 2 - 30},{yb - 30} L{xb - bw / 2},{yb - 30}"
                lx, ly = (xa + xb) / 2 - 60, 32
            elif a == 5:                                 # Ch5 -> Ch3 diagonal (dashed)
                p = f"M{xa - bw / 2 + 20},{ya - bh / 2} L{xb + bw / 2 - 20},{yb + bh / 2}"
                lx, ly = (xa + xb) / 2 + 48, (ya + yb) / 2 + 12
            else:
                xm = (xa + bw / 2 + xb - bw / 2) / 2
                p = f"M{xa + sx * bw / 2},{ya} L{xm},{ya} L{xm},{yb} L{xb - sx * bw / 2},{yb}"
                lx, ly = xm, yb
        col = GREEN if dashed else NAVY
        out.append(f'<path d="{p}" fill="none" stroke="{col}" stroke-width="{1.8 if dashed else 2.6}"'
                   f'{" stroke-dasharray=\"7 5\"" if dashed else ""} marker-end="url(#rm-arr)"/>')
        if label:
            anchor = "end" if (xa == xb) else ("start" if a == 5 else "middle")
            for k, ln in enumerate(label if isinstance(label, list) else [label]):
                out.append(f'<text x="{lx}" y="{ly + 18 * k}" text-anchor="{anchor}" font-size="14" font-style="italic" '
                           f'fill="{GREEN}">{ln}</text>')

    for a, b, l in EDGES:
        edge(a, b, False, l)
    for a, b, l in DASHED:
        edge(a, b, True, l)
    for n, (cx, cy, title, lines) in ROADMAP.items():
        c = by[n]; href = f"ch{n}/{c['slug']}.html"
        x, y = cx - bw / 2, cy - bh / 2
        out.append(f'<a href="{href}" class="rm-node"><title>{html.escape(c["title"])}</title>'
                   f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="10" fill="#fff" stroke="{NAVY}" '
                   f'stroke-width="2" filter="url(#rm-sh)"/>'
                   f'<rect x="{x}" y="{y}" width="8" height="{bh}" rx="3" fill="{RED}"/>'
                   f'<text x="{x + 22}" y="{y + 26}" font-size="13" font-weight="700" fill="{RED}" '
                   f'letter-spacing=".08em">CHAPTER {n}</text>'
                   f'<text x="{x + 22}" y="{y + 52}" font-size="19" font-weight="700" fill="{NAVY}">{html.escape(title)}</text>'
                   + "".join(f'<text x="{x + 22}" y="{y + 76 + 20 * i}" font-size="14.5" fill="#555">{html.escape(t)}</text>'
                             for i, t in enumerate(lines)) + '</a>')
    out.append('</svg>')
    legend = ('<div class="roadmap-legend"><span class="solid"></span> builds on &nbsp;&nbsp;'
              '<span class="dash"></span> feeds results into &nbsp;&nbsp;· click a box to open the slides</div>')
    return "```{=html}\n<div class=\"roadmap-wrap\">" + "\n".join(out) + "</div>\n" + legend + "\n```\n"


def updates():
    """Hand-written announcements from tools/chapters.py (not the git log)."""
    if not UPDATES:
        return ""
    items = "\n".join(f"- **{d}** — {m}" for d, m in UPDATES)
    return f"## Recent updates\n\n{items}\n"


def contents():
    out = ['---', 'title: "Slide contents"', 'subtitle: "Every slide of every chapter — use the search box (top right) to find a topic"', '---', '']
    for ch in CHAPTERS:
        d, s = f"ch{ch['n']}", ch["slug"]
        out.append(f"## {ch['n']}. {ch['title']}\n")
        for k, lev, t, _ in slides(f"{d}/{s}.qmd"):
            link = f"[{t}]({d}/{s}.html#/{hash_(f'{d}/{s}.qmd', k)})"
            out.append(f"\n**{link}**\n" if lev == 1 else f"- {link}")
        out.append("")
    return "\n".join(out)


def problems():
    out = ['---', 'title: "Homework problems"', 'subtitle: "All problems by chapter, linked to the slide where they are posed"', '---', '']
    for ch in CHAPTERS:
        d, s = f"ch{ch['n']}", ch["slug"]
        probs = [(k, t, b) for k, lev, t, b in slides(f"{d}/{s}.qmd") if t.startswith("Problem")]
        if not probs:
            continue
        out.append(f"## {ch['n']}. {ch['title']}\n")
        for k, t, b in probs:
            label = re.sub(r"\s+", " ", t.replace("(homework)", "")).strip()
            label = re.sub(r"^(Problem #\d+) ", r"\1 — ", label)
            out.append(f"- **[{label}]({d}/{s}.html#/{hash_(f'{d}/{s}.qmd', k)})** — {summary(b)}")
        out.append("")
    out.append(f"*Starter code for each problem is at the end of the chapter's Colab notebook.*")
    return "\n".join(out)


# MATLAB snippets that use variables defined on an earlier slide: prepend that setup to the .m file
MATLAB_SETUP = {
    (1, "State-space form"): [
        "% --- setup from the slide 'Example 1.3 in code' ---",
        "q = 100; V = 100; cAi = 1; Ti = 350; rhoCp = 239; dH = -5e4; ER = 8750; k0 = 7.2e10; UA = 5e4;",
        "f = @(t, x, Tc) [q/V*(cAi - x(1)) - k0*exp(-ER/x(2))*x(1);",
        "                 q/V*(Ti - x(2)) - dH/rhoCp*k0*exp(-ER/x(2))*x(1) + UA/(V*rhoCp)*(Tc - x(2))];",
        "[~, x] = ode45(@(t, x) f(t, x, 290), [0 50], [0.95; 320]);  xs = x(end, :)';",
        "k = k0*exp(-ER/xs(2));  kp = k*ER/xs(2)^2;",
        "A = [-q/V - k, -kp*xs(1); -dH*k/rhoCp, -q/V - UA/(V*rhoCp) - dH*kp*xs(1)/rhoCp];",
        "B = [0; UA/(V*rhoCp)];",
        "% ---"],
    (5, "Example 5.13 in code"): [
        "% --- setup from the slide 'Margins in code' ---",
        "G = tf([-6 3], conv([10 1],[5 1]));",
        "[Ku,~,wc] = margin(G);   Pu = 2*pi/wc;",
        "% ---"],
}


def matlab_blocks(qmd):
    """[(slide index, title, code)] for every ```{.matlab} block of a deck."""
    out = []
    for k, lev, t, body in slides(qmd):
        i = 0
        while i < len(body):
            if body[i].strip() in ("```{.matlab}", "```matlab"):
                j = i + 1
                while not body[j].strip().startswith("```"):
                    j += 1
                out.append((k, t, "\n".join(body[i + 1:j]).rstrip()))
                i = j
            i += 1
    return out


def slugify(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", re.sub(r"\$[^$]*\$", "", t)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")[:40].rstrip("_")


def matlab():
    page = ['---', 'title: "MATLAB scripts"',
            'subtitle: "Every MATLAB code tab of the slides, by chapter — download a chapter and run the scripts in MATLAB"', '---', '',
            'Each script is self-contained (`clear; close all` at the top) and named after its slide. '
            'All need the **Control System Toolbox**; scripts with `syms` also need the **Symbolic Math Toolbox**. '
            'The Python versions of the same calculations are in each chapter\'s Colab notebook.', '']
    stamp = (2026, 1, 1, 0, 0, 0)                               # fixed zip timestamps: no spurious diffs
    for ch in CHAPTERS:
        n, d, s = ch["n"], f"ch{ch['n']}", ch["slug"]
        blocks = matlab_blocks(f"{d}/{s}.qmd")
        if not blocks:
            continue
        mdir = ROOT / d / "matlab"; mdir.mkdir(exist_ok=True)
        for old in mdir.glob("*.m"):
            old.unlink()
        files, seen = [], {}
        for k, t, code in blocks:
            name = f"{d}_{k:02d}_{slugify(t)}"
            seen[name] = seen.get(name, 0) + 1
            if seen[name] > 1:
                name += f"_{seen[name]}"
            tbx = "Control System Toolbox" + (", Symbolic Math Toolbox" if re.search(r"\bsyms\b", code) else "")
            setup = MATLAB_SETUP.get((n, t), [])
            text = "\n".join([f"%% Ch.{n} — {t}", f"% Process Dynamics and Control, SeoulTech — slide {k + 1}",
                              f"% {SITE}{d}/{s}.html#/{hash_(f'{d}/{s}.qmd', k)}", f"% Requires: {tbx}", "", "clear; close all; clc", "",
                              *setup, *([""] if setup else []), code, ""])
            (mdir / f"{name}.m").write_text(text, encoding="utf-8")
            files.append((k, t, name, text, tbx))
        zpath = mdir / f"{d}_matlab.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for _, _, name, text, _ in files:
                z.writestr(zipfile.ZipInfo(f"{d}_matlab/{name}.m", stamp), text)
        page.append(f"## {n}. {ch['title']}\n")
        page.append(f'[⬇ Download all ({len(files)} script{"s" if len(files) > 1 else ""}, zip)]({d}/matlab/{d}_matlab.zip){{.btn-dl download=""}}\n')
        for k, t, name, text, tbx in files:
            sym = " · needs Symbolic Math Toolbox" if "Symbolic" in tbx else ""
            page.append(f"### {t}\n")
            page.append(f'[slide {k + 1}]({d}/{s}.html#/{hash_(f"{d}/{s}.qmd", k)}) · [⬇ {name}.m]({d}/matlab/{name}.m){{download=""}}{sym}\n')
            page.append(f'```{{.matlab filename="{name}.m"}}\n{text.rstrip()}\n```\n')
    return "\n".join(page)


def readme():
    rows = ["| Chapter | Topics | Slides | PDF | Notebook |", "|:--|:--|:--|:--|:--|"]
    for ch in CHAPTERS:
        d, s = f"ch{ch['n']}", ch["slug"]
        rows.append(f"| [{ch['n']}. {ch['title']}]({d}) | {', '.join(ch['topics'])} | [HTML]({SITE}{d}/{s}.html) | "
                    f"[slides]({d}/{s}.pdf) · [handout]({d}/{s}_handout.pdf) | [Colab]({COLAB}/{d}/{s}.ipynb) |")
    p = ROOT / "README.md"; txt = p.read_text(encoding="utf-8")
    block = "<!-- chapters:start -->\n" + "\n".join(rows) + "\n<!-- chapters:end -->"
    txt = re.sub(r"<!-- chapters:start -->.*?<!-- chapters:end -->", lambda _: block, txt, flags=re.S)
    p.write_text(txt, encoding="utf-8")


def write(name, text):
    p = ROOT / name
    if not p.exists() or p.read_text(encoding="utf-8") != text:
        p.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    write("_chapters.md", cards())
    write("_roadmap.md", roadmap())
    write("_updates.md", updates())
    write("contents.qmd", contents())
    write("problems.qmd", problems())
    write("matlab.qmd", matlab())
    readme()
    print("index pieces written for", len(CHAPTERS), "chapters")
