#!/usr/bin/env bash
# Build one chapter: figures, notebook, site, PDF, handout.
#   tools/build_chapter.sh ch4 ch4_stability "Ch. 4 Stability of Closed-Loop Systems"
set -euo pipefail
ch=$1; name=$2; title=$3
( cd "$ch" && python make_figures.py && python build_notebook.py )
quarto render
python tools/make_pdf.py "docs/$ch/$name.html" "$ch/$name.pdf" "$title"
python tools/make_handout.py "$ch/$name.pdf" "$ch/${name}_handout.pdf" "$title"
quarto render            # copies the PDFs into docs/
