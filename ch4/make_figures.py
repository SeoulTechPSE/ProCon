"""Figures for Ch.4 Stability of Closed-Loop Systems (python-control + matplotlib)."""
import numpy as np
import matplotlib.pyplot as plt
import control as ct
from pathlib import Path

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

NAVY, RED, GREEN, GRAY = "#333399", "#C00000", "#2E7D32", "#888888"
BR = ["#1f4e9c", "#C00000", "#2E7D32", "#E07B00"]   # branch colors
plt.rcParams.update({
    "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.bbox": "tight", "mathtext.fontset": "cm",
})


def locus(num, den, kmax=1e4, n=4000, kmin=0.0):
    """Root-locus branches of den + K*num = 0, tracked continuously."""
    num, den = np.atleast_1d(num).astype(float), np.atleast_1d(den).astype(float)
    num = np.concatenate([np.zeros(len(den) - len(num)), num])
    ks = np.concatenate([[kmin], np.logspace(-4, np.log10(kmax), n)])
    prev = np.sort_complex(np.roots(den + ks[0] * num))
    R = [prev]
    for k in ks[1:]:
        r = np.roots(den + k * num)
        out = np.empty_like(prev); used = set()
        for i, p in enumerate(prev):                     # nearest-neighbour matching
            d = [abs(p - q) if j not in used else np.inf for j, q in enumerate(r)]
            j = int(np.argmin(d)); used.add(j); out[i] = r[j]
        R.append(out); prev = out
    return ks, np.array(R)


def plot_locus(ax, num, den, kmax=1e4, title=None, xlim=None, ylim=None, marks=None):
    ks, R = locus(num, den, kmax)
    for i in range(R.shape[1]):
        ax.plot(R[:, i].real, R[:, i].imag, color=BR[i % 4], lw=1.8)
    p = np.roots(den); z = np.roots(num) if len(np.atleast_1d(num)) > 1 else []
    ax.plot(p.real, p.imag, "x", color="k", ms=9, mew=2)
    if len(z):
        ax.plot(np.real(z), np.imag(z), "o", mfc="white", mec="k", ms=9, mew=1.8)
    ax.axhline(0, color=GRAY, lw=0.6, ls=":"); ax.axvline(0, color=GRAY, lw=0.8, ls=":")
    if xlim: ax.set_xlim(xlim)
    if ylim: ax.set_ylim(ylim)
    ax.set_xlabel("Real axis"); ax.set_ylabel("Imaginary axis")
    if title: ax.set_title(title)
    if marks:
        for K, lab in marks:
            r = np.roots(np.polyadd(den, K * np.atleast_1d(num)))
            ax.plot(r.real, r.imag, "s", color=RED, ms=6, zorder=5)
            if lab:
                rr = r[np.argmax(r.imag)]
                ax.annotate(lab, (rr.real, rr.imag), xytext=(10, 6), textcoords="offset points", color=RED)
    return ax


P = np.polymul  # alias

# -------------------------------------------------------------------- F1 s-plane
def fig_splane():
    fig = plt.figure(figsize=(11, 4.6))
    ax = fig.add_axes([0.04, 0.1, 0.36, 0.82])
    ax.axvspan(0, 3, color=RED, alpha=0.08); ax.axvspan(-3, 0, color=NAVY, alpha=0.06)
    ax.axhline(0, color="k", lw=0.8); ax.axvline(0, color="k", lw=1.2)
    ax.text(-1.5, 2.2, "Stable\n(LHP)", ha="center", color=NAVY, fontsize=14)
    ax.text(1.5, 2.2, "Unstable\n(RHP)", ha="center", color=RED, fontsize=14)
    pts = {"a": [-1.5 + 0j], "b": [1.2 + 0j], "c": [-0.8 + 1.4j, -0.8 - 1.4j], "d": [0.15 + 1.5j, 0.15 - 1.5j]}
    for lab, ps in pts.items():
        for q in ps:
            ax.plot(q.real, q.imag, "x", color="k", ms=10, mew=2)
        ax.annotate(f"({lab})", (ps[0].real, ps[0].imag), xytext=(6, 6), textcoords="offset points")
    ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_xlabel("Re $s$"); ax.set_ylabel("Im $s$")
    ax.set_title("Closed-loop poles in the $s$-plane")
    t = np.linspace(0, 8, 400)
    sys = {"a": ct.tf(1.5, [1, 1.5]), "b": ct.tf(1, [1, -1.2]),
           "c": ct.tf(0.64 + 1.96, [1, 1.6, 0.64 + 1.96]), "d": ct.tf(2.2725, [1, -0.3, 2.2725])}
    names = {"a": "negative real", "b": "positive real", "c": "complex, Re < 0", "d": "complex, Re > 0"}
    for i, (lab, g) in enumerate(sys.items()):
        a2 = fig.add_axes([0.48 + 0.26 * (i % 2), 0.56 - 0.47 * (i // 2), 0.22, 0.34])
        tt = t if lab in "ac" else np.linspace(0, 20 if lab == "d" else 2.5, 600)
        _, y = ct.step_response(g, tt)
        a2.plot(tt, y, color=NAVY if lab in "ac" else RED, lw=1.8)
        a2.set_title(f"({lab}) {names[lab]}", fontsize=11); a2.set_yticks([]); a2.set_xticks([])
        a2.set_xlabel("time", fontsize=10)
    fig.savefig(OUT / "f01_splane.png"); plt.close(fig)


# -------------------------------------------------------------------- Ex 4.2B
def fig_ex42():
    den = P(P([1, 1], [1, 2]), [1, 3])
    fig, ax = plt.subplots(figsize=(6.4, 5))
    plot_locus(ax, [1], den, kmax=600, xlim=(-7, 1.5), ylim=(-5, 5),
               marks=[(60, r"$K_c=60,\ s=\pm j\sqrt{11}$")])
    ax.set_title(r"$1+K_c\,\dfrac{1}{(s+1)(s+2)(s+3)}=0$")
    fig.savefig(OUT / "f02_ex42_rlocus.png"); plt.close(fig)


# -------------------------------------------------------------------- Ex 4.4 dead time
def fig_ex44():
    t = np.linspace(0, 60, 3000)
    G = ct.tf(0.8, [5, 1])
    num10, den10 = ct.pade(2, 10)
    D10 = ct.tf(num10, den10)
    num1, den1 = ct.pade(2, 1)
    D1 = ct.tf(num1, den1)
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    for ax, (D, lab) in zip(axs, [(D10, r"exact delay $e^{-2s}$ (10th-order Padé)"),
                                  (D1, r"1st-order Padé $\frac{1-s}{1+s}$")]):
        for K, c in [(5.0, NAVY), (5.73, GREEN), (6.5, RED)]:
            T = ct.feedback(K * G * D, 1)
            _, y = ct.step_response(T, t)
            ax.plot(t, y, color=c, lw=1.6, label=f"$K_c={K}$")
        ax.set_title(lab, fontsize=12); ax.set_xlabel("time")
        ax.axhline(0, color=GRAY, lw=0.5)
        ax.set_ylim(-1.5, 2.5)
    axs[0].set_ylabel("$c(t)$"); axs[1].legend(loc="upper right", fontsize=10)
    fig.savefig(OUT / "f03_ex44_pade.png"); plt.close(fig)


# -------------------------------------------------------------------- gallery Ex 4.6
def fig_gallery():
    fig, axs = plt.subplots(1, 4, figsize=(15, 3.9))
    cases = [([1], P([1, 2], [1, 1]), r"(a) $\dfrac{1}{(s+1)(s+2)}$"),
             ([1], [1, 4, 5], r"(b) $\dfrac{1}{s^2+4s+5}$"),
             ([1, 2.5], P([1, 2], [1, 1]), r"(c) $\dfrac{s+2.5}{(s+1)(s+2)}$"),
             ([1, 3], [1, 4, 5], r"(d) $\dfrac{s+3}{s^2+4s+5}$")]
    for ax, (n, d, ttl) in zip(axs, cases):
        plot_locus(ax, n, d, kmax=500, xlim=(-6, 1), ylim=(-2.5, 2.5), title=ttl)
        ax.set_ylabel("")
    # breakaway / break-in on (c)
    for x in [-1.634, -3.366]:
        axs[2].plot(x, 0, "D", color=RED, ms=6)
    axs[2].annotate("−1.634", (-1.634, 0), xytext=(-5, -22), textcoords="offset points", color=RED, fontsize=10)
    axs[2].annotate("−3.366", (-3.366, 0), xytext=(-20, -22), textcoords="offset points", color=RED, fontsize=10)
    # departure angle on (d)
    axs[3].annotate("", xy=(-2 + 0.7 * np.cos(-3 * np.pi / 4), -1 + 0.7 * np.sin(-3 * np.pi / 4)), xytext=(-2, -1),
                    arrowprops=dict(arrowstyle="->", color=RED, lw=1.8))
    axs[3].text(-3.1, -2.2, r"$\phi_{dep}=-\frac{3\pi}{4}$", color=RED)
    axs[0].set_ylabel("Imaginary axis")
    fig.tight_layout(); fig.savefig(OUT / "f04_gallery.png"); plt.close(fig)


# -------------------------------------------------------------------- zero effect, 3rd order
def fig_zero():
    den = P(P([1, 1], [1, 2]), [1, 3])
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.2))
    plot_locus(axs[0], [1], den, kmax=600, xlim=(-7, 1.5), ylim=(-6, 6),
               title=r"no zero: $n-m=3$, unstable for $K_c>60$")
    plot_locus(axs[1], [1, 1.5], den, kmax=2000, xlim=(-7, 1.5), ylim=(-6, 6),
               title=r"zero at $-1.5$: $n-m=2$, $\gamma=-2.25$")
    plot_locus(axs[2], P([1, 1.5], [1, 2.5]), den, kmax=2000, xlim=(-7, 1.5), ylim=(-6, 6),
               title=r"zeros at $-1.5,-2.5$: $n-m=1$")
    axs[1].axvline(-2.25, color=GREEN, ls="--", lw=1)
    for a in axs[1:]: a.set_ylabel("")
    fig.tight_layout(); fig.savefig(OUT / "f05_zero_effect.png"); plt.close(fig)


# -------------------------------------------------------------------- Ex 4.3B
def fig_ex43():
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.4))
    for ax, tI, lim in [(axs[0], 0.2, ((-5.5, 2), (-6, 6))), (axs[1], 0.6, ((-2, 0.4), (-2.5, 2.5)))]:
        num = [tI, 1]; den = tI * np.array(P([1, 0], [1, 2, 1]))
        plot_locus(ax, num, den, kmax=5000, xlim=lim[0], ylim=lim[1],
                   title=fr"$\tau_I={tI}$" + ("  (unstable for large $K_c$)" if tI < 0.5 else "  (stable for all $K_c$)"))
    Kc = 0.2 / (0.5 - 0.2)   # tauI = Kc/(2(1+Kc)) -> Kc = 2 tauI/(1-2tauI)
    r = np.roots(np.polyadd(0.2 * np.array(P([1, 0], [1, 2, 1])), Kc * np.array([0.2, 1])))
    axs[0].plot(r.real, r.imag, "s", color=RED); axs[0].annotate(fr"$K_c={Kc:.3f}$", (0, r.imag.max()),
                                                                xytext=(8, 0), textcoords="offset points", color=RED)
    axs[1].set_ylabel("")
    fig.tight_layout(); fig.savefig(OUT / "f06_ex43_rlocus.png"); plt.close(fig)


# -------------------------------------------------------------------- zeta geometry & specs
def zeta_lines(ax, z, R):
    th = np.arccos(z)
    for sgn in [1, -1]:
        ax.plot([0, -R * np.cos(th)], [0, sgn * R * np.sin(th)], color=GREEN, ls="--", lw=1.2)


def fig_ex47():
    den = P([2, 1], [4, 1])
    fig, ax = plt.subplots(figsize=(6.2, 4.8))
    plot_locus(ax, [1], den, kmax=50, xlim=(-0.8, 0.1), ylim=(-0.8, 0.8))
    zeta_lines(ax, 0.7, 1.2)
    K = 127 / 98
    r = np.roots(np.polyadd(den, [K]))
    ax.plot(r.real, r.imag, "s", color=RED, ms=7)
    ax.annotate(r"$K_c=1.30$" + "\n" + r"$s=-0.375\pm 0.383j$", (r.real[0], abs(r.imag[0])), xytext=(14, 4),
                textcoords="offset points", color=RED)
    ax.text(-0.75, 0.62, r"$\zeta=0.7$", color=GREEN)
    ax.set_title(r"$1+K_c\,\dfrac{1}{(2s+1)(4s+1)}=0$")
    fig.savefig(OUT / "f07_ex47.png"); plt.close(fig)


def fig_ex48():
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.4))
    for ax, tI, lim in [(axs[0], 3.0, ((-1.5, 0.1), (-1, 1))), (axs[1], 2 / 3, ((-3.6, 0.2), (-1.6, 1.6)))]:
        num = 0.5 * np.array([tI, 1]); den = tI * np.array(P([1, 0], [2, 1]))
        plot_locus(ax, num, den, kmax=500, xlim=lim[0], ylim=lim[1], title=fr"$\tau_I={tI:.3g}$ min")
        zeta_lines(ax, 0.7, 4)
    axs[0].text(-1.4, 0.6, "all closed-loop poles real\n→ $\\zeta=0.7$ not attainable", color=RED, fontsize=11)
    tI = 2 / 3
    for K, lab in [(0.5552, "0.555"), (7.2048, "7.20")]:
        r = np.roots(np.polyadd(tI * np.array(P([1, 0], [2, 1])), K * 0.5 * np.array([tI, 1])))
        axs[1].plot(r.real, r.imag, "s", color=RED)
        axs[1].annotate(fr"$K_c={lab}$", (r.real[0], abs(r.imag[0])), xytext=(8, 6), textcoords="offset points",
                        color=RED)
    axs[1].set_ylabel("")
    fig.tight_layout(); fig.savefig(OUT / "f08_ex48.png"); plt.close(fig)


def fig_spec():
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    z = np.linspace(0.05, 0.99, 200)
    axs[0].plot(z, 100 * np.exp(-np.pi * z / np.sqrt(1 - z ** 2)), color=NAVY, lw=2)
    axs[0].plot(0.7, 4.6, "o", color=RED); axs[0].annotate(r"$\zeta=0.7$: 4.6 %", (0.7, 4.6), xytext=(10, 15),
                                                           textcoords="offset points", color=RED)
    axs[0].set_xlabel(r"damping ratio $\zeta$"); axs[0].set_ylabel("overshoot  %OS")
    axs[0].set_title(r"$\%OS = 100\,\exp(-\pi\zeta/\sqrt{1-\zeta^2})$")
    ax = axs[1]
    th = np.arccos(0.7); R = 3
    poly = np.array([[-1, 0], [-1, -R * np.tan(th)], [-R, -R * np.tan(th)], [-R, R * np.tan(th)], [-1, R * np.tan(th)]])
    # admissible region: Re s < -sigma and inside zeta-wedge
    xs = np.linspace(-R, -1, 100)
    ax.fill_between(xs, xs * np.tan(th), -xs * np.tan(th), color=GREEN, alpha=0.15)
    zeta_lines(ax, 0.7, R * 1.42)
    ax.axvline(-1, color=NAVY, ls="--"); ax.text(-0.95, 2.4, r"$\sigma=\zeta\omega_n=4/t_s$", color=NAVY)
    ax.text(-2.6, 0.2, "design\nregion", color=GREEN, fontsize=12)
    ax.text(-2.9, -0.6, r"$\zeta\geq 0.7$", color=GREEN, fontsize=12)
    ax.axhline(0, color=GRAY, lw=0.6); ax.axvline(0, color=GRAY, lw=0.8)
    ax.set_xlim(-R, 0.5); ax.set_ylim(-3, 3); ax.set_xlabel("Re $s$"); ax.set_ylabel("Im $s$")
    ax.set_title("Pole-placement region from specs")
    fig.tight_layout(); fig.savefig(OUT / "f09_specs.png"); plt.close(fig)


# -------------------------------------------------------------------- RHP zero
def fig_rhpz():
    den = P([1, 1], [2, 1]); num = [-1, 1]
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    # den + K*num = 2s^2 + (3-K)s + (1+K)
    ks, R = locus(num, den, kmax=40)
    for i in range(2):
        axs[0].plot(R[:, i].real, R[:, i].imag, color=BR[i], lw=1.8)
    axs[0].plot([-1, -0.5], [0, 0], "x", color="k", ms=9, mew=2)
    axs[0].plot([1], [0], "o", mfc="white", mec="k", ms=9, mew=1.8)
    r = np.roots([2, 0, 4]); axs[0].plot(r.real, r.imag, "s", color=RED)
    axs[0].annotate(r"$K_c=3,\ s=\pm j\sqrt{2}$", (0, np.sqrt(2)), xytext=(-150, 14), textcoords="offset points", color=RED)
    axs[0].axhline(0, color=GRAY, lw=0.6, ls=":"); axs[0].axvline(0, color=GRAY, lw=0.8, ls=":")
    axs[0].set_xlim(-3, 4); axs[0].set_ylim(-2.5, 2.5)
    axs[0].set_title(r"$1+K_c\,\dfrac{-s+1}{(s+1)(2s+1)}=0$  (RHP zero at $s=+1$)")
    axs[0].set_xlabel("Real axis"); axs[0].set_ylabel("Imaginary axis")
    t = np.linspace(0, 10, 500)
    _, y = ct.step_response(ct.tf(num, den), t)
    axs[1].plot(t, y, color=NAVY, lw=2); axs[1].axhline(0, color=GRAY, lw=0.6)
    axs[1].set_title("open-loop step response: inverse response"); axs[1].set_xlabel("time")
    fig.tight_layout(); fig.savefig(OUT / "f10_rhp_zero.png"); plt.close(fig)


if __name__ == "__main__":
    for f in [fig_splane, fig_ex42, fig_ex44, fig_gallery, fig_zero, fig_ex43, fig_ex47, fig_ex48, fig_spec, fig_rhpz]:
        f(); print("ok", f.__name__)
