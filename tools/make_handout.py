"""A4 handout: 3 slides per page on the left, ruled note space on the right.

    python tools/make_handout.py ch4/ch4_stability.pdf ch4/ch4_stability_handout.pdf "Ch. 4 Stability of Closed-Loop Systems"
"""
import sys
import pymupdf

src_path, out_path = sys.argv[1], sys.argv[2]
title = sys.argv[3] if len(sys.argv) > 3 else ""

A4W, A4H = 595.28, 841.89
M_L, M_R, M_T, M_B = 36, 30, 48, 40          # page margins (pt)
PER_PAGE, GAP = 3, 22
NAVY, GRAY = (0.2, 0.2, 0.6), (0.72, 0.72, 0.72)

src = pymupdf.open(src_path)
sw, sh = src[0].rect.width, src[0].rect.height
cell_h = (A4H - M_T - M_B - GAP * (PER_PAGE - 1)) / PER_PAGE
slide_w = min(330, cell_h * sw / sh)
slide_h = slide_w * sh / sw
note_x0 = M_L + slide_w + 16
note_x1 = A4W - M_R

out = pymupdf.open()
n_pages = (src.page_count + PER_PAGE - 1) // PER_PAGE
for p in range(n_pages):
    page = out.new_page(width=A4W, height=A4H)
    page.insert_text((M_L, 30), "Process Dynamics and Control", fontsize=9, color=NAVY, fontname="helv")
    if title:
        tw = pymupdf.get_text_length(title, fontname="helv", fontsize=9)
        page.insert_text((A4W - M_R - tw, 30), title, fontsize=9, color=NAVY, fontname="helv")
    page.draw_line((M_L, 36), (A4W - M_R, 36), color=NAVY, width=0.6)
    for k in range(PER_PAGE):
        i = p * PER_PAGE + k
        if i >= src.page_count:
            break
        y0 = M_T + k * (cell_h + GAP) + (cell_h - slide_h) / 2
        r = pymupdf.Rect(M_L, y0, M_L + slide_w, y0 + slide_h)
        page.show_pdf_page(r, src, i)                       # vector, text stays selectable
        page.draw_rect(r, color=GRAY, width=0.6)
        # ruled note lines
        y = y0 + 14
        while y <= y0 + slide_h + 0.1:
            page.draw_line((note_x0, y), (note_x1, y), color=GRAY, width=0.4)
            y += 17
    foot = f"{p + 1} / {n_pages}"
    fw = pymupdf.get_text_length(foot, fontname="helv", fontsize=8)
    page.insert_text(((A4W - fw) / 2, A4H - 18), foot, fontsize=8, color=GRAY, fontname="helv")

out.set_metadata({"title": f"Process Dynamics and Control — {title} (handout)", "author": "Kee-Youn Yoo"})
out.save(out_path, garbage=4, deflate=True)
print(out_path, out.page_count, "pages")
