"""Print formulas.qmd (rendered to _site/formulas.html) as A4 formula sheets.

    python3 tools/make_formulas.py            # after `quarto render formulas.qmd`

Writes formulas/chN_formulas.pdf (one page per chapter) and formulas/ProCon_formulas.pdf.
Set MATHJAX_DIR=/path/to/mathjax/es5 to serve MathJax locally (offline builds).
"""
import asyncio, os, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "_site" / "formulas.html"
OUT = ROOT / "formulas"
MJ = os.environ.get("MATHJAX_DIR")

PRINT_CSS = """
@page { size: A4; margin: 10mm 13mm 13mm 13mm; }
header, nav, #quarto-header, #quarto-margin-sidebar, #TOC, .quarto-title-block, .fs-dl,
footer, .nav-footer, #quarto-back-to-top, .anchorjs-link { display: none !important; }
body { font-size: 10pt; line-height: 1.32; color: #111; }
main.content { margin: 0 !important; padding: 0 !important; max-width: none !important; width: 100% !important; grid-column: 1 / -1 !important; }
#quarto-content { display: block !important; }
section.level1 { break-before: page; }
section.level1:first-of-type { break-before: auto; }
section.level1.fs-hide { display: none !important; }
body.fs-single section.level1 { break-before: auto; }
h1 { font-size: 14pt; color: #fff; background: #1f3a68; padding: 4px 9px; margin: 0 0 7px 0; border: 0; }
.fs-cols { }
.fs-cols p, .fs-cols ul { margin: 0 0 5px 0; }
.fs-cols ul { padding-left: 1.1em; }
.fs-cols strong { color: #1f3a68; }
.fs-cols table { break-inside: avoid; font-size: 9.2pt; margin: 2px 0 6px 0 !important; width: auto !important; }
.fs-cols table td, .fs-cols table th { padding: 1px 5px !important; }
.fs-cols div.math, .fs-cols mjx-container[display="true"] { margin: 3px 0 !important; }
"""

FOOT = dict(display_header_footer=True, header_template="<span></span>",
            footer_template='<div style="font-size:7pt;color:#777;width:100%;padding:0 13mm;display:flex;justify-content:space-between">'
                            '<span>Process Dynamics and Control · Kee-Youn Yoo, SeoulTech</span>'
                            '<span>seoultechpse.github.io/ProCon</span></div>')

async def route(r):
    u = r.request.url
    if MJ and "mathjax" in u and "/es5/" in u:
        p = pathlib.Path(MJ) / u.split("/es5/")[1].split("?")[0]
        if p.exists():
            await r.fulfill(path=str(p)); return
    await r.continue_()

async def main():
    OUT.mkdir(exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.route("**/*", route)
        await pg.goto(SRC.as_uri())
        await pg.wait_for_function("window.MathJax && MathJax.startup && MathJax.startup.promise")
        await pg.evaluate("MathJax.startup.promise")
        await pg.add_style_tag(content=PRINT_CSS)
        await pg.emulate_media(media="print")
        # scale each chapter so it fills one A4 page (printable height ≈ 274 mm)
        await pg.set_viewport_size({"width": 694, "height": 1000})   # 184 mm at 96 dpi
        await pg.evaluate("""() => {
            const H = 274 / 25.4 * 96 - 12;
            document.querySelectorAll('section.level1').forEach(s => {
                s.style.zoom = 1;
                let z = Math.min(1.35, H / s.getBoundingClientRect().height);
                for (let k = 0; k < 8; k++) {          // text re-wraps when zoomed: shrink until it fits
                    s.style.zoom = z.toFixed(3);
                    const h = s.getBoundingClientRect().height;
                    if (h <= H) break;
                    z *= Math.max(0.9, H / h) * 0.995;
                }
            });
        }""")
        n = await pg.evaluate("document.querySelectorAll('section.level1').length")
        await pg.pdf(path=str(OUT / "ProCon_formulas.pdf"), format="A4", print_background=True, prefer_css_page_size=True, **FOOT)
        await pg.evaluate("document.body.classList.add('fs-single')")
        for i in range(n):
            await pg.evaluate("""i => document.querySelectorAll('section.level1').forEach((s, j) =>
                s.classList.toggle('fs-hide', j !== i))""", i)
            await pg.pdf(path=str(OUT / f"ch{i+1}_formulas.pdf"), format="A4", print_background=True, prefer_css_page_size=True, **FOOT)
        await b.close()
    try:
        from pypdf import PdfReader
        for f in sorted(OUT.glob("*.pdf")):
            k = len(PdfReader(f).pages)
            print(f"{f.name}: {k} page(s)" + ("" if f.name.startswith("ProCon") or k == 1 else "  <-- more than one page"))
    except ImportError:
        pass

asyncio.run(main())
