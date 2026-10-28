"""Generate the site's index pieces from tools/chapters.py (run automatically as Quarto pre-render).

    python3 tools/build_index.py

Writes
    _chapters.md   chapter cards for index.qmd (topics, thumbnail, links, widgets, PDF sizes, last update)
    _updates.md    announcements (UPDATES in tools/chapters.py) for index.qmd
    contents.qmd   every slide title of every deck, linked (searchable: reveal decks are not indexed)
    problems.qmd   homework problems of all chapters, linked to their slides
    README.md      chapter table between <!-- chapters:start --> and <!-- chapters:end -->
Only the standard library is required (Pillow is used for thumbnails when available).
"""
import html
import re
import subprocess
import sys
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


def slides(qmd):
    """[(index, level, title, body_lines)] with reveal's numeric hash index (title slide = 0)."""
    out, fence, k = [], False, 0
    for line in (ROOT / qmd).read_text(encoding="utf-8").split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and re.match(r"^#{1,2} ", line):
            k += 1
            out.append([k, len(line.split(" ")[0]), clean_title(line.split(" ", 1)[1]), []])
        elif out:
            out[-1][3].append(line)
    return out


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
            link = f"[{t}]({d}/{s}.html#/{k})"
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
            out.append(f"- **[{label}]({d}/{s}.html#/{k})** — {summary(b)}")
        out.append("")
    out.append(f"*Starter code for each problem is at the end of the chapter's Colab notebook.*")
    return "\n".join(out)


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
    write("_updates.md", updates())
    write("contents.qmd", contents())
    write("problems.qmd", problems())
    readme()
    print("index pieces written for", len(CHAPTERS), "chapters")
