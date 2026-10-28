"""Print a rendered reveal.js deck to PDF (one slide per page), keeping SVG math.

    pip install playwright pymupdf && playwright install chromium
    python tools/make_pdf.py docs/ch4/ch4_stability.html ch4/ch4_stability.pdf "4. Stability of Closed-Loop Systems"
"""
import sys, asyncio, pathlib
from playwright.async_api import async_playwright
import pymupdf


async def main(html, out):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1280, "height": 800})
        await pg.goto(pathlib.Path(html).resolve().as_uri() + "?print-pdf")
        await pg.wait_for_function("window.MathJax && MathJax.startup && MathJax.startup.promise")
        await pg.evaluate("MathJax.startup.promise")
        await pg.wait_for_timeout(2000)
        await pg.emulate_media(media="print")
        await pg.pdf(path=out, width="1280px", height="800px", print_background=True,
                     margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        await b.close()


html, out = sys.argv[1], sys.argv[2]
asyncio.run(main(html, out))
title = sys.argv[3] if len(sys.argv) > 3 else ""
d = pymupdf.open(out)
d.set_metadata({"title": f"Process Dynamics and Control — {title}", "author": "Kee-Youn Yoo"})
d.save(out + ".tmp", garbage=4, deflate=True)
d.close(); pathlib.Path(out + ".tmp").replace(out)
print(out)
