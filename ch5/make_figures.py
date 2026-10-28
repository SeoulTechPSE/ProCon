"""Figures for Ch.5 Frequency-Response Analysis & Design (python-control + matplotlib)."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter
import control as ct
from pathlib import Path

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

NAVY, RED, GREEN, ORANGE, GRAY = "#333399", "#C00000", "#2E7D32", "#E07B00", "#888888"
SEQ = ["#1f4e9c", "#3b6fc0", "#2E7D32", "#E07B00", "#C00000", "#7b1fa2"]
plt.rcParams.update({
    "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.bbox": "tight", "mathtext.fontset": "cm",
    "axes.grid": True, "grid.color": "#e3e3e3", "grid.linewidth": 0.6,
})


# ---------------------------------------------------------------- helpers
def freqresp(G, w, delay=0.0):
    """Complex G(jw) (optionally times e^{-j w delay}); phase unwrapped (deg)."""
    g = np.array([complex(G(1j * wi)) for wi in w]) * np.exp(-1j * w * delay)
    mag = np.abs(g)
    ph = np.degrees(np.unwrap(np.angle(g)))
    return g, mag, ph




def bode(ax_m, ax_p, G, w, delay=0.0, **kw):
    _, mag, ph = freqresp(G, w, delay)
    ax_m.loglog(w, mag, **kw)
    ax_p.semilogx(w, ph, **kw)
    return mag, ph


def nyq(ax, G, w, delay=0.0, color=NAVY, lw=1.8, neg=True, arrows=True, label=None):
    g, _, _ = freqresp(G, w, delay)
    ax.plot(g.real, g.imag, color=color, lw=lw, label=label)
    if neg:
        ax.plot(g.real, -g.imag, color=color, lw=lw * 0.8, ls="--", alpha=0.6)
    if arrows:
        for frac in (0.35, 0.6):
            i = int(frac * len(w))
            ax.annotate("", xy=(g[i + 1].real, g[i + 1].imag), xytext=(g[i].real, g[i].imag),
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4, mutation_scale=14))
    ax.axhline(0, color=GRAY, lw=0.7); ax.axvline(0, color=GRAY, lw=0.7)
    ax.set_xlabel("Re $G(j\\omega)$"); ax.set_ylabel("Im $G(j\\omega)$")
    return g


def crit(ax):
    ax.plot(-1, 0, "+", color=RED, ms=14, mew=2.2, zorder=6)


def fmt_bode(ax_m, ax_p, ylab_m="AR $=|G(j\\omega)|$"):
    ax_m.set_ylabel(ylab_m); ax_p.set_ylabel("$\\phi$ (deg)"); ax_p.set_xlabel("$\\omega$ (rad/time)")
    ax_m.xaxis.set_major_locator(LogLocator(base=10)); ax_p.xaxis.set_major_locator(LogLocator(base=10))
    ax_m.yaxis.set_major_locator(LogLocator(base=10)); ax_m.yaxis.set_minor_formatter(NullFormatter())


# ---------------------------------------------------------------- f01 sinusoidal response
def fig_sine():
    G = ct.tf(2, [1.5, 1])
    fig, axs = plt.subplots(1, 2, figsize=(13, 3.9))
    for ax, w in zip(axs, (3, 10)):
        t = np.linspace(0, 15, 6000)
        u = np.sin(w * t)
        _, y = ct.forced_response(G, t, u)
        ar = 2 / np.sqrt(1 + (1.5 * w) ** 2); ph = np.degrees(-np.arctan(1.5 * w))
        ax.plot(t, u, color=NAVY, lw=1.4, label="input $u=\\sin\\omega t$")
        ax.plot(t, y, color=RED, lw=1.9, label="output $y(t)$")
        ax.axhline(ar, color=RED, ls=":", lw=1); ax.axhline(-ar, color=RED, ls=":", lw=1)
        ax.set_xlim(0, 8 if w == 3 else 4); ax.set_ylim(-1.15, 1.15)
        ax.set_title(f"$\\omega={w}$:  AR $={ar:.3f}$,  $\\phi={ph:.1f}^\\circ$")
        ax.set_xlabel("time")
    axs[0].legend(loc="lower right", fontsize=10, framealpha=0.95)
    fig.suptitle("$G(s)=\\dfrac{2}{1.5s+1}$: after the transient, the output is a sine of the same frequency",
                 y=1.04, fontsize=13)
    fig.tight_layout(); fig.savefig(OUT / "f01_sine_response.png"); plt.close(fig)


# ---------------------------------------------------------------- f02 first order
def fig_first_order():
    G = ct.tf(1, [2, 1]); w = np.logspace(-2, 1.3, 600)
    fig = plt.figure(figsize=(13, 4.8))
    am = fig.add_axes([0.06, 0.55, 0.42, 0.38]); ap = fig.add_axes([0.06, 0.1, 0.42, 0.38], sharex=am)
    bode(am, ap, G, w, color=NAVY, lw=2)
    wc = 0.5
    am.loglog([w[0], wc, w[-1]], [1, 1, wc / w[-1]], color=ORANGE, ls="--", lw=1.4, label="asymptotes")
    am.plot(wc, 1 / np.sqrt(2), "o", color=RED); am.annotate("$K_p/\\sqrt{2}$ at $\\omega=1/\\tau_p$", (wc, 0.707),
                                                            xytext=(-175, -34), textcoords="offset points", color=RED)
    am.text(0.9, 0.035, "slope $-1$\n($-20$ dB/dec)", color=ORANGE)
    ap.plot(wc, -45, "o", color=RED); ap.axhline(-90, color=GRAY, ls=":")
    ap.annotate("$-45^\\circ$", (wc, -45), xytext=(10, 4), textcoords="offset points", color=RED)
    for a in (am, ap): a.axvline(wc, color=GRAY, ls=":", lw=1)
    am.legend(loc="lower left", fontsize=10); fmt_bode(am, ap); am.set_title("Bode plot ($K_p=1,\\ \\tau_p=2$)")
    plt.setp(am.get_xticklabels(), visible=False)
    an = fig.add_axes([0.58, 0.1, 0.38, 0.83])
    nyq(an, G, np.logspace(-3, 3, 3000))
    an.plot(0.5, -0.5, "o", color=RED); an.annotate("$\\omega=1/\\tau_p$", (0.5, -0.5), xytext=(8, -16),
                                                   textcoords="offset points", color=RED)
    an.annotate("$\\omega=0$", (1, 0), xytext=(-8, 10), textcoords="offset points", ha="right")
    an.annotate("$\\omega\\to\\infty$", (0, 0), xytext=(6, 10), textcoords="offset points")
    an.set_aspect("equal"); an.set_xlim(-0.2, 1.2); an.set_ylim(-0.7, 0.7)
    an.set_title("Nyquist plot: semicircle ($\\omega\\geq 0$ solid)")
    fig.savefig(OUT / "f02_first_order.png"); plt.close(fig)


# ---------------------------------------------------------------- f03 second order family
def fig_second_order():
    tau = 2; w = np.logspace(-2, 2, 800)
    fig = plt.figure(figsize=(13, 4.8))
    am = fig.add_axes([0.06, 0.55, 0.42, 0.38]); ap = fig.add_axes([0.06, 0.1, 0.42, 0.38], sharex=am)
    an = fig.add_axes([0.58, 0.1, 0.38, 0.83])
    zs = [1.2, 1.0, 0.8, 0.6, 0.4, 0.2]
    for z, c in zip(zs, SEQ):
        G = ct.tf(1, [tau ** 2, 2 * z * tau, 1])
        bode(am, ap, G, w, color=c, lw=1.7, label=f"$\\zeta={z}$")
        nyq(an, G, np.logspace(-3, 3, 4000), color=c, lw=1.5, arrows=False)
    for a in (am, ap): a.axvline(1 / tau, color=GRAY, ls=":", lw=1)
    am.set_ylim(1e-4, 5); am.legend(fontsize=9, ncol=2, loc="lower left")
    am.text(8, 2e-2, "slope $-2$", color=GRAY)
    fmt_bode(am, ap); am.set_title("$G=\\dfrac{1}{\\tau^2s^2+2\\zeta\\tau s+1},\\ \\tau=2$")
    plt.setp(am.get_xticklabels(), visible=False)
    an.set_aspect("equal"); an.set_xlim(-1.6, 1.6); an.set_ylim(-2.7, 2.7); crit(an)
    an.set_title("Nyquist: crosses $-90^\\circ$ at $|G|=K/2\\zeta$")
    fig.savefig(OUT / "f03_second_order.png"); plt.close(fig)


# ---------------------------------------------------------------- f04 building blocks: lead, integrator, lag+integrator
def fig_blocks1():
    w = np.logspace(-2, 1.3, 600)
    cases = [(ct.tf([2, 1], 1), "lead  $\\tau_ds+1,\\ \\tau_d=2$"),
             (ct.tf(1, [1, 0]), "integrator  $K/s,\\ K=1$"),
             (ct.tf(1, [2, 1, 0]), "lag + integrator  $\\dfrac{1}{s(2s+1)}$")]
    fig, axs = plt.subplots(3, 3, figsize=(14, 7.2), gridspec_kw=dict(height_ratios=[1, 1, 1.35]))
    for j, (G, ttl) in enumerate(cases):
        bode(axs[0, j], axs[1, j], G, w, color=NAVY, lw=2)
        axs[0, j].set_title(ttl); axs[1, j].set_xlabel("$\\omega$")
        axs[0, j].set_xticklabels([])
    axs[0, 0].set_ylabel("AR"); axs[1, 0].set_ylabel("$\\phi$ (deg)")
    axs[0, 0].text(1.5, 2, "slope $+1$", color=GRAY); axs[0, 1].text(0.5, 5, "slope $-1$", color=GRAY)
    axs[1, 1].set_ylim(-100, -80)
    # Nyquist
    a = axs[2, 0]; g = freqresp(cases[0][0], np.logspace(-3, 1.2, 400))[0]
    a.plot(g.real, g.imag, color=NAVY, lw=2); a.annotate("", xy=(1, 14), xytext=(1, 8),
                                                         arrowprops=dict(arrowstyle="-|>", color=NAVY))
    a.set_xlim(-1, 2.5); a.set_ylim(-2, 20); a.text(1.1, 0.5, "$\\omega=0$")
    a = axs[2, 1]; a.plot([0, 0], [-10, 0], color=NAVY, lw=2)
    a.annotate("", xy=(0, -1), xytext=(0, -5), arrowprops=dict(arrowstyle="-|>", color=NAVY))
    a.set_xlim(-1, 1); a.set_ylim(-10, 1); a.text(0.05, -9.5, "$\\omega\\to 0$")
    a = axs[2, 2]; g = freqresp(cases[2][0], np.logspace(-1.7, 2, 600))[0]
    a.plot(g.real, g.imag, color=NAVY, lw=2); a.axvline(-2, color=ORANGE, ls="--", lw=1.2)
    a.text(-1.95, -45, "asymptote\nRe $=-\\tau=-2$", color=ORANGE, fontsize=10)
    a.set_xlim(-3, 0.3); a.set_ylim(-60, 2)
    for a in axs[2]:
        a.axhline(0, color=GRAY, lw=0.7); a.axvline(0, color=GRAY, lw=0.7); a.set_xlabel("Re")
    axs[2, 0].set_ylabel("Im")
    fig.tight_layout(); fig.savefig(OUT / "f04_blocks_lead_int.png"); plt.close(fig)


# ---------------------------------------------------------------- f05 dead time and FOPDT
def fig_blocks2():
    w = np.logspace(-2, 1.5, 2000)
    fig, axs = plt.subplots(2, 3, figsize=(14, 5.4), gridspec_kw=dict(width_ratios=[1.15, 1.15, 1]))
    G1 = ct.tf(1, 1); G2 = ct.tf(1, [10, 1])
    # dead time
    _, m, p = freqresp(G1, w, 2.0)
    axs[0, 0].semilogx(w, m, color=NAVY, lw=2); axs[0, 0].set_ylim(0.5, 1.5); axs[0, 0].set_title("dead time $e^{-\\theta s},\\ \\theta=2$")
    axs[1, 0].semilogx(w, p, color=NAVY, lw=2); axs[1, 0].set_ylim(-3000, 50)
    axs[1, 0].text(0.012, -2500, "$\\phi=-\\theta\\omega$ (rad): unbounded lag", color=RED)
    # FOPDT
    _, m, p = freqresp(G2, w, 2.0); _, m0, p0 = freqresp(G2, w, 0.0)
    axs[0, 1].loglog(w, m, color=NAVY, lw=2); axs[0, 1].set_title("FOPDT $\\dfrac{e^{-2s}}{10s+1}$")
    axs[1, 1].semilogx(w, p0, color=GRAY, ls="--", lw=1.4, label="without delay")
    axs[1, 1].semilogx(w, p, color=NAVY, lw=2, label="with delay"); axs[1, 1].set_ylim(-3000, 50)
    axs[1, 1].legend(fontsize=10, loc="lower left")
    for j in (0, 1):
        axs[0, j].set_xticklabels([]); axs[1, j].set_xlabel("$\\omega$")
    axs[0, 0].set_ylabel("AR"); axs[1, 0].set_ylabel("$\\phi$ (deg)")
    # Nyquist (merged column)
    gs = axs[0, 2].get_gridspec(); axs[0, 2].remove(); axs[1, 2].remove()
    an = fig.add_subplot(gs[:, 2])
    th = np.linspace(0, 2 * np.pi, 400); an.plot(np.cos(th), np.sin(th), color=GRAY, lw=1.2, ls=":", label="$e^{-\\theta s}$: unit circle")
    g = freqresp(G2, np.logspace(-3, 1.5, 6000), 2.0)[0]
    an.plot(g.real, g.imag, color=NAVY, lw=1.8, label="FOPDT: spiral to 0")
    an.axhline(0, color=GRAY, lw=0.7); an.axvline(0, color=GRAY, lw=0.7); crit(an)
    an.set_aspect("equal"); an.set_xlim(-1.15, 1.15); an.set_ylim(-1.15, 1.15)
    an.legend(fontsize=10, loc="upper left"); an.set_xlabel("Re"); an.set_ylabel("Im"); an.set_title("Nyquist")
    fig.tight_layout(); fig.savefig(OUT / "f05_blocks_deadtime.png"); plt.close(fig)


# ---------------------------------------------------------------- f06 asymptotic sketch Ex 5.9
def fig_asymptotic():
    G = ct.tf([5, 1], np.polymul([10, 1], [2, 1])); w = np.logspace(-3, 1, 600)
    fig, (am, ap) = plt.subplots(2, 1, figsize=(10.5, 5.6), sharex=True)
    _, m, p = freqresp(G, w)
    am.semilogx(w, 20 * np.log10(m), color=NAVY, lw=2.2, label="exact")
    # asymptote: 0 dB to 0.1, -20 dB/dec to 0.2, 0 slope (zero) to 0.5, -20 dB/dec
    def asym(wi):
        db = 0.0
        db += -20 * np.log10(np.maximum(wi / 0.1, 1))
        db += +20 * np.log10(np.maximum(wi / 0.2, 1))
        db += -20 * np.log10(np.maximum(wi / 0.5, 1))
        return db
    am.semilogx(w, asym(w), color=ORANGE, ls="--", lw=1.8, label="straight-line asymptotes")
    for wc, lab in [(0.1, "pole\n$1/10$"), (0.2, "zero\n$1/5$"), (0.5, "pole\n$1/2$")]:
        am.axvline(wc, color=GRAY, ls=":", lw=1); ap.axvline(wc, color=GRAY, ls=":", lw=1)
        am.text(wc * 1.05, 2, lab, fontsize=10, color=GRAY, va="bottom")
    am.text(0.0015, -8, "slope 0", color=ORANGE); am.text(0.115, -13, "$-1$", color=ORANGE)
    am.text(0.26, -8.3, "$0$", color=ORANGE); am.text(1.1, -8, "slope $-1$\n(high-freq. gain $5/20$)", color=ORANGE, fontsize=11)
    am.set_ylabel("AR (dB)"); am.set_ylim(-36, 9); am.legend(loc="lower left", fontsize=10)
    am.set_title("Ex 5.9: $G(s)=\\dfrac{5s+1}{(10s+1)(2s+1)}$ — add the pieces")
    ap.semilogx(w, p, color=NAVY, lw=2.2)
    for wc, sgn, c in [(0.1, -1, RED), (0.2, +1, GREEN), (0.5, -1, RED)]:
        ap.semilogx(w, sgn * np.degrees(np.arctan(w / wc)), color=c, lw=1, ls="--", alpha=0.8)
    ap.text(0.0013, 30, "$+\\tan^{-1}5\\omega$ (zero)", color=GREEN, fontsize=10)
    ap.text(0.0013, -60, "$-\\tan^{-1}10\\omega,\\ -\\tan^{-1}2\\omega$ (poles)", color=RED, fontsize=10)
    ap.set_ylabel("$\\phi$ (deg)"); ap.set_xlabel("$\\omega$ (rad/time)"); ap.set_ylim(-95, 95)
    fig.tight_layout(); fig.savefig(OUT / "f06_asymptotic_ex59.png"); plt.close(fig)


# ---------------------------------------------------------------- f07 Ex 5.11 step + root locus
G510 = ct.tf([-6, 3], np.polymul([10, 1], [5, 1]))


def fig_ex511_time():
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.2), gridspec_kw=dict(width_ratios=[1.4, 1]))
    t = np.linspace(0, 100, 3000)
    for K, c in [(0.5, NAVY), (1.5, GREEN), (2.5, RED)]:
        T = ct.feedback(K * G510, 1); _, y = ct.step_response(T, t)
        axs[0].plot(t, y, color=c, lw=1.9, label=f"$K_c={K}$")
        axs[0].axhline(T.dcgain(), color=c, ls=":", lw=1)
    axs[0].set_xlabel("time (s)"); axs[0].set_ylabel("$y(t)$"); axs[0].legend(loc="upper left", fontsize=10, ncol=3)
    axs[0].set_ylim(-0.45, 2.75)
    axs[0].set_title("P control, unit set-point step: inverse response + offset")
    T25 = ct.feedback(2.5 * G510, 1); _, y25 = ct.step_response(T25, t)
    pk = [i for i in range(1, len(t) - 1) if y25[i] > y25[i - 1] and y25[i] > y25[i + 1] and t[i] > 30][:2]
    axs[0].annotate("", xy=(t[pk[1]], 2.2), xytext=(t[pk[0]], 2.2), arrowprops=dict(arrowstyle="<->", color=RED))
    axs[0].text((t[pk[0]] + t[pk[1]]) / 2, 2.27, "$P_u=15.2$ s", color=RED, ha="center")
    # root locus: den + K num = 50s^2 + (15-6K)s + (1+3K)
    ks = np.concatenate([np.linspace(0, 40, 4000)])
    R = np.array([np.sort_complex(np.roots([50, 15 - 6 * k, 1 + 3 * k])) for k in ks])
    a = axs[1]
    up = np.array([r[np.argmax(r.imag)] for r in R]); lo = np.conj(up)
    real = np.iscomplex(R).sum(1) == 0
    a.plot(R[real, 0].real, 0 * R[real, 0].real, ".", color="#1f4e9c", ms=1.5)
    a.plot(R[real, 1].real, 0 * R[real, 1].real, ".", color="#1f4e9c", ms=1.5)
    a.plot(up[~real].real, up[~real].imag, color="#1f4e9c", lw=1.8); a.plot(lo[~real].real, lo[~real].imag, color="#1f4e9c", lw=1.8)
    a.plot([-0.1, -0.2], [0, 0], "x", color="k", ms=9, mew=2); a.plot([0.5], [0], "o", mfc="white", mec="k", ms=9, mew=1.8)
    a.plot([0, 0], [0.4123, -0.4123], "s", color=RED); a.annotate("$K_u=2.5,\\ s=\\pm j0.412$", (0, 0.41),
                                                                xytext=(10, 8), textcoords="offset points", color=RED)
    a.axvline(0, color=GRAY, lw=0.8); a.axhline(0, color=GRAY, lw=0.6)
    a.set_xlim(-0.25, 1.25); a.set_ylim(-0.8, 0.8); a.set_xlabel("Re $s$"); a.set_ylabel("Im $s$")
    a.set_title("root locus (RHP zero at $s=0.5$)")
    fig.tight_layout(); fig.savefig(OUT / "f07_ex511_time_rlocus.png"); plt.close(fig)


# ---------------------------------------------------------------- f08 Ex 5.11 Bode & Nyquist at Kc=1
def fig_ex511_freq():
    w = np.logspace(-2, 1, 1000); wc = 0.41231
    fig = plt.figure(figsize=(13, 4.9))
    am = fig.add_axes([0.06, 0.55, 0.44, 0.38]); ap = fig.add_axes([0.06, 0.1, 0.44, 0.38], sharex=am)
    bode(am, ap, G510, w, color=NAVY, lw=2)
    am.plot(wc, 0.4, "o", color=RED); am.axhline(1, color=GRAY, ls="-", lw=0.8)
    am.annotate("$|G(j\\omega_c)|=0.4$", (wc, 0.4), xytext=(14, -6), textcoords="offset points", color=RED)
    ap.axhline(-180, color=RED, ls="--", lw=1); ap.plot(wc, -180, "o", color=RED)
    ap.annotate("$\\omega_c=0.412$", (wc, -180), xytext=(10, 10), textcoords="offset points", color=RED)
    for a in (am, ap): a.axvline(wc, color=RED, ls=":", lw=1)
    fmt_bode(am, ap); am.set_title("Bode plot of $G_{OL}$ with $K_c=1$"); plt.setp(am.get_xticklabels(), visible=False)
    an = fig.add_axes([0.6, 0.1, 0.37, 0.83])
    nyq(an, G510, np.logspace(-3, 2, 5000)); crit(an)
    an.plot(-0.4, 0, "o", color=RED); an.annotate("$-0.4$", (-0.4, 0), xytext=(-4, 10), textcoords="offset points", color=RED)
    an.annotate("$-1$", (-1, 0), xytext=(-24, -18), textcoords="offset points", color=RED)
    an.set_aspect("equal"); an.set_xlim(-1.55, 3.2); an.set_ylim(-2.3, 2.3)
    an.set_title("Nyquist: crosses the real axis at $-0.4K_c$")
    fig.savefig(OUT / "f08_ex511_bode_nyquist.png"); plt.close(fig)


# ---------------------------------------------------------------- f09 GM & PM on Ex 5.12 loop
Ku, Pu = 2.5, 2 * np.pi / np.sqrt(8.5 / 50)
KcZN, tIZN = Ku / 2.2, Pu / 1.2
C_ZN = ct.tf([KcZN * tIZN, KcZN], [tIZN, 0])


def fig_margins():
    L = C_ZN * G510; gm, pm, wc, wg = ct.margin(L)
    w = np.logspace(-2, 1, 1500)
    fig = plt.figure(figsize=(13, 5.1))
    am = fig.add_axes([0.06, 0.55, 0.44, 0.38]); ap = fig.add_axes([0.06, 0.1, 0.44, 0.38], sharex=am)
    _, m, p = freqresp(L, w)
    am.loglog(w, m, color=NAVY, lw=2); ap.semilogx(w, p, color=NAVY, lw=2)
    am.axhline(1, color=GRAY, lw=1); ap.axhline(-180, color=GRAY, lw=1)
    for a in (am, ap):
        a.axvline(wg, color=GREEN, ls=":", lw=1.2); a.axvline(wc, color=RED, ls=":", lw=1.2)
    mc = 1 / gm
    am.annotate("", xy=(wc, mc), xytext=(wc, 1), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.8))
    am.text(wc * 1.25, 2.5, f"GM $=1/{mc:.3f}={gm:.2f}$", color=RED)
    pg = -180 + pm
    ap.annotate("", xy=(wg, pg), xytext=(wg, -180), arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.8))
    ap.text(wg * 0.2, -172, f"PM $={pm:.1f}^\\circ$", color=GREEN)
    ap.text(wg * 0.93, -270, "$\\omega_g$", color=GREEN, ha="right"); ap.text(wc * 1.07, -270, "$\\omega_c$", color=RED)
    am.set_ylim(1e-3, 50); ap.set_ylim(-280, -80)
    fmt_bode(am, ap, "AR$_{OL}$"); am.set_title("Ex 5.12 loop $G_{OL}=G_cG$ (ZN PI)"); plt.setp(am.get_xticklabels(), visible=False)
    an = fig.add_axes([0.6, 0.1, 0.37, 0.83])
    g = freqresp(L, np.logspace(-1.6, 2, 4000))[0]
    an.plot(g.real, g.imag, color=NAVY, lw=2)
    th = np.linspace(0, 2 * np.pi, 300); an.plot(np.cos(th), np.sin(th), color=GRAY, ls="--", lw=1)
    crit(an); an.axhline(0, color=GRAY, lw=0.7); an.axvline(0, color=GRAY, lw=0.7)
    an.plot(-mc, 0, "o", color=RED); an.annotate(f"$-1/\\mathrm{{GM}}=-{mc:.3f}$", (-mc, 0), xytext=(-10, 14),
                                                textcoords="offset points", color=RED)
    gg = complex(L(1j * wg)); an.plot(gg.real, gg.imag, "o", color=GREEN)
    an.plot([0, gg.real], [0, gg.imag], color=GREEN, lw=1.4); an.plot([0, -1], [0, 0], color=GREEN, lw=1.4)
    a0 = np.angle(gg); arc = np.linspace(np.pi, a0 + 2 * np.pi if a0 < 0 else a0, 50)
    an.plot(0.45 * np.cos(arc), 0.45 * np.sin(arc), color=GREEN, lw=1.6)
    an.text(-0.62, -0.28, "PM", color=GREEN)
    an.set_aspect("equal"); an.set_xlim(-1.6, 0.6); an.set_ylim(-1.6, 0.6)
    an.set_xlabel("Re"); an.set_ylabel("Im"); an.set_title("Nyquist: distance from $-1$")
    fig.savefig(OUT / "f09_margins.png"); plt.close(fig)
    return gm, pm, wc, wg


# ---------------------------------------------------------------- f10 Ex 5.12 step y,u
def fig_ex512_step():
    t = np.linspace(0, 120, 3000)
    T = ct.feedback(C_ZN * G510, 1); U = ct.feedback(C_ZN, G510)
    _, y = ct.step_response(T, t); _, u = ct.step_response(U, t)
    fig, ax = plt.subplots(figsize=(8.5, 4))
    ax.plot(t, y, color=NAVY, lw=2, label="$y(t)$"); ax.plot(t, u, color=GREEN, lw=1.7, label="$u(t)$")
    ax.axhline(1, color=GRAY, ls=":")
    i = np.argmax(y); ax.annotate(f"overshoot {100 * (y[i] - 1):.0f} %", (t[i], y[i]), xytext=(20, 4),
                                  textcoords="offset points", color=RED)
    ax.annotate("inverse response", (2.5, y[np.argmin(y[:200])]), xytext=(15, -30), textcoords="offset points",
                color=RED, arrowprops=dict(arrowstyle="->", color=RED))
    ax.set_xlabel("time (s)"); ax.legend(); ax.set_title(f"ZN PI: $K_c={KcZN:.2f},\\ \\tau_I={tIZN:.1f}$ s")
    fig.tight_layout(); fig.savefig(OUT / "f10_ex512_step.png"); plt.close(fig)


# ---------------------------------------------------------------- f11 Ex 5.13 retune by G*
def fig_ex513():
    Gs = ct.tf([tIZN, 1], [tIZN, 0]) * G510
    gm1, _, wc1, _ = ct.margin(Gs)
    w = np.logspace(-2.3, 0.7, 4000); _, m, p = freqresp(Gs, w)
    i135 = np.argmin(abs(p + 135)); wg45 = w[i135]; K45 = 1 / m[i135]
    fig = plt.figure(figsize=(13, 4.9))
    am = fig.add_axes([0.06, 0.55, 0.44, 0.38]); ap = fig.add_axes([0.06, 0.1, 0.44, 0.38], sharex=am)
    am.loglog(w, m, color=NAVY, lw=2); ap.semilogx(w, p, color=NAVY, lw=2)
    am.plot(wc1, 1 / gm1, "o", color=RED); am.annotate(f"$|G^*(j\\omega_c)|={1 / gm1:.3f}\\Rightarrow K_{{cu}}={gm1:.2f}$",
                                                      (wc1, 1 / gm1), xytext=(10, 14), textcoords="offset points", color=RED)
    am.plot(wg45, m[i135], "o", color=GREEN); am.annotate(f"$|G^*|={m[i135]:.3f}\\Rightarrow K_c={K45:.2f}$",
                                                         (wg45, m[i135]), xytext=(-215, -30), textcoords="offset points", color=GREEN)
    ap.axhline(-180, color=RED, ls="--", lw=1); ap.axhline(-135, color=GREEN, ls="--", lw=1)
    ap.text(0.006, -177, "$-180^\\circ$", color=RED); ap.text(0.006, -132, "$-135^\\circ$ (PM $=45^\\circ$)", color=GREEN)
    for a in (am, ap):
        a.axvline(wc1, color=RED, ls=":", lw=1); a.axvline(wg45, color=GREEN, ls=":", lw=1)
    ap.set_ylim(-280, -80); fmt_bode(am, ap, "$|G^*(j\\omega)|$")
    am.set_title(f"Bode plot of $G^*=G\\,(1+1/\\tau_Is)$, $\\tau_I={tIZN:.1f}$ s"); plt.setp(am.get_xticklabels(), visible=False)
    a = fig.add_axes([0.6, 0.1, 0.37, 0.83]); t = np.linspace(0, 120, 3000)
    for K, c, lab in [(KcZN, RED, f"ZN $K_c={KcZN:.2f}$ (GM 1.63, PM 19°)"),
                      (gm1 / 2, ORANGE, f"GM = 2: $K_c={gm1 / 2:.2f}$ (PM 27°)"),
                      (K45, NAVY, f"PM = 45°: $K_c={K45:.2f}$ (GM 3.1)")]:
        _, y = ct.step_response(ct.feedback(K * Gs, 1), t); a.plot(t, y, color=c, lw=1.9, label=lab)
    a.axhline(1, color=GRAY, ls=":"); a.legend(fontsize=9.5, loc="lower right"); a.set_xlabel("time (s)")
    a.set_title("closed-loop set-point step"); a.set_ylim(-0.25, 1.75)
    fig.savefig(OUT / "f11_ex513_retune.png"); plt.close(fig)
    return gm1, wc1, wg45, K45


# ---------------------------------------------------------------- f12 Nyquist for open-loop unstable
def fig_nyq_unstable():
    G = ct.tf(1, [1, -1])
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
    for a, K, c in [(axs[0], 0.5, RED), (axs[1], 2.0, NAVY)]:
        w = np.logspace(-3, 3, 4000); g = K * freqresp(G, w)[0]
        a.plot(g.real, g.imag, color=c, lw=2, label="$\\omega>0$"); a.plot(g.real, -g.imag, color=c, lw=1.5, ls="--", label="$\\omega<0$")
        for frac in (0.45,):
            i = int(frac * len(w))
            a.annotate("", xy=(g[i + 1].real, g[i + 1].imag), xytext=(g[i].real, g[i].imag),
                       arrowprops=dict(arrowstyle="-|>", color=c, lw=1.5, mutation_scale=16))
            a.annotate("", xy=(g[i].real, -g[i].imag), xytext=(g[i + 1].real, -g[i + 1].imag),
                       arrowprops=dict(arrowstyle="-|>", color=c, lw=1.5, mutation_scale=16))
        crit(a); a.axhline(0, color=GRAY, lw=0.7); a.axvline(0, color=GRAY, lw=0.7)
        a.set_aspect("equal"); a.set_xlim(-2.4, 0.6); a.set_ylim(-1.3, 1.3); a.set_xlabel("Re"); a.set_ylabel("Im")
        a.legend(fontsize=9, loc="upper left")
    axs[0].set_title("$K_c=0.5$: $N=0,\\ P=1 \\Rightarrow Z=1$ (unstable)")
    axs[1].set_title("$K_c=2$: $N=-1$ (ccw), $P=1 \\Rightarrow Z=0$ (stable)")
    fig.suptitle("$G_{OL}=\\dfrac{K_c}{s-1}$ (Ex 4.1 with $K=a=1$)", y=1.03)
    fig.tight_layout(); fig.savefig(OUT / "f12_nyquist_unstable.png"); plt.close(fig)


# ---------------------------------------------------------------- f13 Ex 4.4 revisited by Bode
def fig_ex44_bode():
    G = ct.tf(0.8, [5, 1]); w = np.logspace(-2, 1, 1500); _, m, p = freqresp(G, w, 2.0)
    wc = 0.89529; mc = 0.8 / np.sqrt(1 + 25 * wc ** 2)
    fig, (am, ap) = plt.subplots(2, 1, figsize=(8.6, 5.2), sharex=True)
    am.loglog(w, m, color=NAVY, lw=2); ap.semilogx(w, p, color=NAVY, lw=2)
    am.plot(wc, mc, "o", color=RED); am.annotate(f"$|G(j\\omega_c)|={mc:.4f}$\n$K_{{cu}}=1/{mc:.4f}={1 / mc:.2f}$",
                                                (wc, mc), xytext=(-170, -40), textcoords="offset points", color=RED)
    ap.axhline(-180, color=RED, ls="--", lw=1); ap.plot(wc, -180, "o", color=RED)
    ap.annotate("$\\omega_c=0.895$", (wc, -180), xytext=(8, 8), textcoords="offset points", color=RED)
    for a in (am, ap): a.axvline(wc, color=RED, ls=":", lw=1)
    ap.set_ylim(-600, 10); fmt_bode(am, ap); am.set_title("$G=\\dfrac{0.8e^{-2s}}{5s+1}$: exact, no Padé")
    am.set_ylim(0.01, 1.5)
    fig.tight_layout(); fig.savefig(OUT / "f13_ex44_bode.png"); plt.close(fig)


# ---------------------------------------------------------------- f14 PM vs zeta
def fig_pm_zeta():
    z = np.linspace(0.02, 1.0, 300)
    pm = np.degrees(np.arctan(2 * z / np.sqrt(np.sqrt(1 + 4 * z ** 4) - 2 * z ** 2)))
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(z, pm, color=NAVY, lw=2.2, label="exact (2nd-order loop)")
    ax.plot(z, 100 * z, color=ORANGE, ls="--", lw=1.6, label="PM $\\approx 100\\,\\zeta$")
    for zz in (0.4, 0.7):
        pz = np.degrees(np.arctan(2 * zz / np.sqrt(np.sqrt(1 + 4 * zz ** 4) - 2 * zz ** 2)))
        ax.plot(zz, pz, "o", color=RED); ax.annotate(f"$\\zeta={zz}$: {pz:.0f}°", (zz, pz), xytext=(8, -16),
                                                     textcoords="offset points", color=RED)
    ax.set_xlabel("closed-loop damping ratio $\\zeta$"); ax.set_ylabel("phase margin (deg)")
    ax.set_xlim(0, 1); ax.set_ylim(0, 80); ax.legend(loc="upper left")
    ax.set_title("$G_{OL}=\\dfrac{\\omega_n^2}{s(s+2\\zeta\\omega_n)}$")
    fig.tight_layout(); fig.savefig(OUT / "f14_pm_zeta.png"); plt.close(fig)


if __name__ == "__main__":
    for f in [fig_sine, fig_first_order, fig_second_order, fig_blocks1, fig_blocks2, fig_asymptotic,
              fig_ex511_time, fig_ex511_freq, fig_margins, fig_ex512_step, fig_ex513, fig_nyq_unstable,
              fig_ex44_bode, fig_pm_zeta]:
        r = f(); print("ok", f.__name__, r if r is not None else "")
