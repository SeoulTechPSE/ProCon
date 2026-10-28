"""Single source of truth for the course chapters.

tools/build_index.py turns this list into the home-page cards, the slide
contents page, the problem index and the chapter table in README.md.
Add a chapter here (and nowhere else) when a new deck is published.
"""

CHAPTERS = [
    dict(n=1, slug="ch1_dynamics", title="Mathematical Preliminaries & Dynamic Response",
         topics=["Laplace transform", "partial fractions", "poles & zeros", "1st/2nd-order response",
                 "dead time & Padé", "FOPDT approximation"],
         thumb="ch1/figures/f04_poles.png",
         widgets=[("Response explorer", "ch1/interactive/response_explorer.html")]),
    dict(n=2, slug="ch2_analysis", title="Analysis of Single-Loop Control Systems",
         topics=["block diagrams", "closed-loop transfer functions", "P / PI / PD / PID",
                 "offset, reset windup, derivative kick"],
         thumb="ch2/figures/f07_modes.png",
         widgets=[("Closed-loop explorer", "ch2/interactive/loop_explorer.html")]),
    dict(n=3, slug="ch3_tuning", title="Tuning of Single-Loop Control Systems",
         topics=["process reaction curve", "Ziegler–Nichols, Cohen–Coon, ITAE", "direct synthesis", "IMC"],
         thumb="ch3/figures/f05_rule_comparison.png",
         widgets=[("Tuning explorer", "ch3/interactive/tuning_explorer.html")]),
    dict(n=4, slug="ch4_stability", title="Stability of Closed-Loop Systems",
         topics=["characteristic equation", "Routh–Hurwitz", "root locus", "dead time & RHP zeros"],
         thumb="ch4/figures/f02_ex42_rlocus.png",
         widgets=[("Root-locus explorer", "ch4/interactive/rlocus_explorer.html")]),
    dict(n=5, slug="ch5_frequency", title="Frequency-Response Analysis & Design",
         topics=["Bode & Nyquist plots", "Bode/Nyquist stability", "gain & phase margins", "tuning by margins"],
         thumb="ch5/figures/f08_ex511_bode_nyquist.png",
         widgets=[("Frequency-response explorer", "ch5/interactive/freq_explorer.html")]),
    dict(n=6, slug="ch6_multiloop", title="Multi-loop Systems",
         topics=["cascade", "feedforward", "Smith predictor", "ratio control", "RGA & decoupling"],
         thumb="ch6/figures/f06_ex66_decoupling.png",
         widgets=[("Cascade explorer", "ch6/interactive/cascade_explorer.html"),
                  ("RGA explorer", "ch6/interactive/rga_explorer.html")]),
]

SITE = "https://seoultechpse.github.io/ProCon/"
REPO = "SeoulTechPSE/ProCon"
