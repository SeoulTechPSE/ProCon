"""Figures for Ch.6 Multiloop Systems (python-control, matplotlib, exact-delay simulator in blocks.py)."""
import numpy as np
import matplotlib.pyplot as plt
import control as ct
from pathlib import Path
from blocks import FOPDT, Delay, PI, DT, simulate_2x2

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
NAVY, RED, GREEN, ORANGE, GRAY = "#333399", "#C00000", "#2E7D32", "#E07B00", "#888888"
plt.rcParams.update({
    "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150,
    "savefig.bbox": "tight", "mathtext.fontset": "cm", "axes.grid": True,
    "grid.color": "#e3e3e3", "grid.linewidth": 0.6,
})

# Ex 6.1 data
Gp, Gv, GL = ct.tf(0.8, [2, 1]), ct.tf(0.5, [1, 1]), ct.tf(0.75, [1, 1])
KC2 = 18
Gvs, GLs = ct.tf(0.9, [0.1, 1]), ct.tf(0.075, [0.1, 1])        # 9/(s+10), 0.75/(s+10)


def locus(num, den, kmax=1e4, n=3000):
    num = np.concatenate([np.zeros(len(den) - len(num)), num])
    ks = np.concatenate([[0], np.logspace(-4, np.log10(kmax), n)])
    prev = np.sort_complex(np.roots(den)); R = [prev]
    for k in ks[1:]:
        r = np.roots(den + k * num); out = np.empty_like(prev); used = set()
        for i, p in enumerate(prev):
            d = [abs(p - q) if j not in used else np.inf for j, q in enumerate(r)]
            j = int(np.argmin(d)); used.add(j); out[i] = r[j]
        R.append(out); prev = out
    return np.array(R)


def fig_ex61_rlocus():
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.3))
    for ax, tI in zip(axs, (0.05, 0.5, 5)):
        num = 0.72 * np.array([tI, 1.0]); den = tI * np.polymul([1, 0], np.polymul([0.1, 1], [2, 1]))
        R = locus(num, den, kmax=3e3)
        for i, c in enumerate(["#1f4e9c", RED, GREEN]):
            ax.plot(R[:, i].real, R[:, i].imag, color=c, lw=1.8)
        ax.plot([0, -0.5, -10], [0, 0, 0], "x", color="k", ms=9, mew=2)
        ax.plot([-1 / tI], [0], "o", mfc="white", mec="k", ms=9, mew=1.8)
        ax.axvline(0, color=GRAY, lw=0.8); ax.axhline(0, color=GRAY, lw=0.6)
        ax.set_xlim(-15, 10); ax.set_ylim(-20, 20); ax.set_xlabel(r"$\mathrm{Re}\,s$")
        verdict = {0.05: "unstable for large $K_c$", 0.5: "stable for all $K_c$, fast", 5: "stable but slow (pole near 0)"}[tI]
        ax.set_title(rf"$\tau_I={tI}$: {verdict}")
    axs[0].set_ylabel(r"$\mathrm{Im}\,s$")
    fig.suptitle(r"$1+K_c\,\dfrac{\tau_Is+1}{\tau_Is}\,\dfrac{0.9}{0.1s+1}\,\dfrac{0.8}{2s+1}=0$", y=1.05)
    fig.tight_layout(); fig.savefig(OUT / "f01_ex61_rlocus.png"); plt.close(fig)


def fig_ex61_response(Kc=3, tI=0.5):
    C = ct.tf([Kc * tI, Kc], [tI, 0]); t = np.linspace(0, 30, 3001)
    load_n = ct.minreal(GL * Gp / (1 + C * Gv * Gp), verbose=False)
    load_c = ct.minreal(GLs * Gp / (1 + C * Gvs * Gp), verbose=False)
    sp_n = ct.feedback(C * Gv * Gp, 1); sp_c = ct.feedback(C * Gvs * Gp, 1)
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.2))
    for ax, (tn, tc), ttl in zip(axs, [(load_n, load_c), (sp_n, sp_c)],
                                 ["unit step in the load $L$ (fuel-gas pressure)", "unit step in the set point $R$"]):
        yn = ct.step_response(tn, t)[1]; yc = ct.step_response(tc, t)[1]
        ax.plot(t, yn, color=RED, lw=2, label="single loop (no cascade)")
        ax.plot(t, yc, color=NAVY, lw=2, label=rf"cascade, $K_{{c2}}={KC2}$")
        ax.set_title(ttl); ax.set_xlabel("time"); ax.legend(loc="upper right")
        if "load" in ttl:
            ax.annotate(f"peak {yn.max():.3f}", (t[np.argmax(yn)], yn.max()), xytext=(14, -2), textcoords="offset points", color=RED)
            ax.annotate(f"peak {yc.max():.3f}", (t[np.argmax(yc)], yc.max()), xytext=(14, 12), textcoords="offset points", color=NAVY)
    axs[0].set_ylabel(r"$C(t)$")
    fig.suptitle(rf"Ex 6.1: primary PI $K_c={Kc},\ \tau_I={tI}$", y=1.02)
    fig.tight_layout(); fig.savefig(OUT / "f02_ex61_response.png"); plt.close(fig)


def fig_ex67_ff():
    GLd = ct.tf(1.2, [5, 1]); C = ct.tf([1.5, 3], [0.5, 0]); t = np.linspace(0, 20, 4001)
    K = -1.2 / 0.72
    cases = [("feedback only", ct.tf(0, 1), RED),
             (rf"+ static FF  $G_{{FF}}={K:.2f}$", ct.tf(K, 1), ORANGE),
             (rf"+ lead-lag FF  $G_{{FF}}={K:.2f}\,\dfrac{{2s+1}}{{5s+1}}$", ct.tf([2 * K, K], [5, 1]), NAVY)]
    fig, ax = plt.subplots(figsize=(9, 4.4))
    for lab, Gff, c in cases:
        T = ct.minreal((GLd + Gff * Gvs * Gp) / (1 + C * Gvs * Gp), verbose=False)
        y = ct.step_response(T, t)[1]
        ax.plot(t, y, color=c, lw=2, label=f"{lab}   (IAE {np.trapezoid(abs(y), t):.3f})")
    ax.axhline(0, color=GRAY, lw=0.8); ax.set_xlabel("time"); ax.set_ylabel(r"$C(t)$")
    ax.set_title(r"unit load step, $G_L=\dfrac{1.2}{5s+1}$, plant $G_v^*G_p=\dfrac{0.72}{(0.1s+1)(2s+1)}$")
    ax.legend(loc="upper right", fontsize=10.5)
    fig.tight_layout(); fig.savefig(OUT / "f03_ex67_ff.png"); plt.close(fig)


def smith_run(Kc, tI, smith, theta=2.0, theta_model=2.0, tf=40):
    G = FOPDT(0.8, 5, theta); M0 = FOPDT(0.8, 5, 0); Md = Delay(theta_model); c = PI(Kc, tI)
    n = int(tf / DT) + 1; y = ym0 = ymd = 0.0; ys = np.zeros(n)
    for k in range(n):
        u = c(1 - y - ((ym0 - ymd) if smith else 0.0))
        y = G(u); ym0 = M0(u); ymd = Md(ym0); ys[k] = y
    return np.arange(n) * DT, ys


def fig_ex68_smith():
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.3))
    a = axs[0]
    for (Kc, tI, sm, lab, c) in [(2.58, 5.85, False, r"PI (ZN) $K_c=2.58$, no predictor", ORANGE),
                                 (5, 5, False, r"PI $K_c=5,\ \tau_I=5$, no predictor", RED),
                                 (5, 5, True, r"PI $K_c=5,\ \tau_I=5$ + Smith predictor", NAVY)]:
        t, y = smith_run(Kc, tI, sm); a.plot(t, y, color=c, lw=2, label=lab)
    a.set_ylim(-0.5, 2.5); a.set_title(r"plant $0.8e^{-2s}/(5s+1)$ (Ex 4.4): set-point step")
    a.legend(loc="upper right", fontsize=10); a.set_xlabel("time"); a.set_ylabel(r"$Y(t)$")
    a = axs[1]
    for th, c in [(2.0, NAVY), (2.6, ORANGE), (3.0, RED)]:
        t, y = smith_run(5, 5, True, theta=th); a.plot(t, y, color=c, lw=2, label=rf"true $\theta={th}$ (model 2.0)")
    a.set_title("model error: dead time underestimated"); a.legend(loc="lower right", fontsize=10)
    a.set_xlabel("time"); a.set_ylim(-0.1, 1.5)
    fig.tight_layout(); fig.savefig(OUT / "f04_ex68_smith.png"); plt.close(fig)


def fig_rga_blend():
    x = np.linspace(0, 1, 201)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(x, 1 - x, color=NAVY, lw=2.2, label=r"$\lambda_{x,m_1}=1-x$")
    ax.plot(x, x, color=RED, lw=2.2, ls="--", label=r"$\lambda_{x,m_2}=x$")
    ax.axvspan(0, 0.5, color=NAVY, alpha=0.06); ax.axvspan(0.5, 1, color=RED, alpha=0.06)
    ax.text(0.25, 0.55, "pair  $x$–$m_1$,  $F$–$m_2$", color=NAVY, ha="center")
    ax.text(0.75, 0.55, "pair  $x$–$m_2$,  $F$–$m_1$", color=RED, ha="center")
    for xv, lab in [(0.0099, "Ex 6.5a"), (0.9, "Ex 6.5b")]:
        ax.plot(xv, 1 - xv, "o", color="k"); ax.annotate(lab, (xv, 1 - xv), xytext=(8, -14), textcoords="offset points")
    ax.set_xlabel(r"product composition $x=m_1/(m_1+m_2)$"); ax.set_ylabel(r"relative gain")
    ax.set_title("blending: RGA depends on the operating point"); ax.legend(loc="lower left")
    fig.tight_layout(); fig.savefig(OUT / "f05_rga_blend.png"); plt.close(fig)


G66 = [[(0.07, 12, 3), (-0.05, 15, 1)], [(0.1, 11, 4), (-0.15, 10, 2)]]
KC66 = (0.586 / 0.07 * (12 / 3) ** 0.916, -0.586 / 0.15 * (10 / 2) ** 0.916)
TI66 = (12 / (1.03 - 0.165 * 3 / 12), 10 / (1.03 - 0.165 * 2 / 10))
DEC = [("no decoupling", None, None, RED),
       ("static decouplers 0.71, 0.67", 0.714, 0.667, ORANGE),
       ("dynamic decouplers (lead-lag + delay)", (0.714, 12, 15, 0), (0.667, 10, 11, 2), NAVY)]


def fig_ex66():
    fig, axs = plt.subplots(2, 2, figsize=(13, 6.6), sharex=True)
    for col, (r1, r2) in enumerate([(1, 0), (0, 1)]):
        for lab, D12, D21, c in DEC:
            t, c1, c2, _, _ = simulate_2x2(G66, KC66, TI66, D12, D21, r1, r2, tf=80)
            axs[0, col].plot(t, c1, color=c, lw=1.9, label=lab); axs[1, col].plot(t, c2, color=c, lw=1.9)
        axs[0, col].set_title(rf"step in $x_D$ set point" if r1 else rf"step in $x_B$ set point")
        axs[1, col].set_xlabel("time")
    axs[0, 0].set_ylabel(r"$x_D$"); axs[1, 0].set_ylabel(r"$x_B$")
    axs[0, 0].legend(loc="lower right", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "f06_ex66_decoupling.png"); plt.close(fig)


if __name__ == "__main__":
    for f in (fig_ex61_rlocus, fig_ex61_response, fig_ex67_ff, fig_ex68_smith, fig_rga_blend, fig_ex66):
        f(); print("ok", f.__name__)
