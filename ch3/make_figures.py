"""Figures for Ch.3 Tuning of Single-Loop Control Systems."""
import numpy as np
import matplotlib.pyplot as plt
import control as ct
from pathlib import Path
from tuning import RULES, pid_tf, fit_two_point, fit_tangent, imc, simc, simc_integrating, simulate, pi_law, relay_law

OUT = Path(__file__).parent / "figures"; OUT.mkdir(exist_ok=True)
NAVY, RED, GREEN, ORANGE, GRAY, PURPLE = "#333399", "#C00000", "#2E7D32", "#E07B00", "#888888", "#7b1fa2"
COL = [NAVY, RED, GREEN, ORANGE, PURPLE]
plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150, "savefig.bbox": "tight",
                     "mathtext.fontset": "cm", "axes.grid": True, "grid.color": "#e3e3e3", "grid.linewidth": 0.6})

y_ = lambda sysm, t: np.asarray(ct.step_response(sysm, t).outputs, float).ravel()
GT = ct.tf(1, np.polymul(np.polymul([2, 1], [1, 1]), [0.5, 1]))          # "true" plant of Ex 3.6
GVV = ct.tf(0.5858 * np.array([-0.3549, 1]), [0.1858, 0.8627, 1])          # Van de Vusse reactor
KCU, _, WC, _ = ct.margin(GVV); TU = 2 * np.pi / WC


def fig_prc():
    t = np.linspace(0, 16, 16001); y = y_(GT, t)
    K, tau, th = fit_two_point(t, y); Kt, taut, tht = fit_tangent(t, y)
    fo = lambda K, tau, th: np.where(t < th, 0, K * (1 - np.exp(-(t - th) / tau)))
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.plot(t, y, color="k", lw=2.4, label=r"measured: $\dfrac{1}{(2s+1)(s+1)(0.5s+1)}$")
    ax.plot(t, fo(K, tau, th), color=NAVY, lw=2, ls="--", label=rf"two-point fit: $\theta={th:.2f},\ \tau={tau:.2f}$")
    ax.plot(t, fo(Kt, taut, tht), color=RED, lw=1.8, ls=":", label=rf"tangent fit: $\theta={tht:.2f},\ \tau={taut:.2f}$")
    dy = np.gradient(y, t); i = int(np.argmax(dy))
    tl = np.array([tht, tht + taut]); ax.plot(tl, [0, 1], color=RED, lw=1, alpha=0.6)
    for frac, c in [(0.283, NAVY), (0.632, NAVY)]:
        ti = t[np.argmax(y >= frac)]; ax.plot([0, ti, ti], [frac, frac, 0], color=c, lw=0.8, ls=":")
        ax.text(ti + 0.1, 0.03, rf"$t_{{{int(frac * 100)}}}={ti:.2f}$", color=c, fontsize=11)
    ax.plot(t[i], y[i], "o", color=RED, ms=5); ax.text(t[i] + 0.3, y[i] - 0.06, "inflection", color=RED, fontsize=10)
    ax.set_xlim(0, 16); ax.set_ylim(-0.02, 1.1); ax.set_xlabel("time"); ax.set_ylabel(r"$C_m/(K\,\Delta P)$")
    ax.legend(loc="lower right", fontsize=10.5); ax.set_title("Process-reaction curve and two FOPDT fits")
    fig.tight_layout(); fig.savefig(OUT / "f01_prc_fit.png"); plt.close(fig)


def sim_sat(Kc, umax=None, tf=8, dt=1e-3):
    """P control of the Van de Vusse model with optional actuator saturation (unit set-point step)."""
    A, B, C, D = ct.ssdata(ct.tf2ss(GVV)); A, B, C = np.asarray(A), np.asarray(B).ravel(), np.asarray(C).ravel()
    x = np.zeros(A.shape[0]); n = int(tf / dt); ys = np.zeros(n)
    for k in range(n):
        yk = C @ x + float(np.asarray(D).ravel()[0]) * 0; ys[k] = yk
        u = Kc * (1 - yk)
        if umax is not None: u = np.clip(u, -umax, umax)
        x = x + dt * (A @ x + B * u)
    return np.arange(n) * dt, ys


def fig_ultimate():
    fig, axs = plt.subplots(2, 2, figsize=(11, 6.2), sharex=True)
    cases = [(2.5, None, r"(a) $K_c<K_{cu}$: decaying"), (KCU, None, r"(b) $K_c=K_{cu}$: sustained, period $T_u$"),
             (4.5, None, r"(c) $K_c>K_{cu}$: growing (no saturation)"), (4.5, 3.0, r"(d) $K_c>K_{cu}$ with valve saturation")]
    for ax, (K, um, ttl) in zip(axs.ravel(), cases):
        t, y = sim_sat(K, um); ax.plot(t, y, color=RED if K > KCU else NAVY, lw=2); ax.set_title(ttl, fontsize=12)
        ax.set_ylim(-1.5, 2.6)
        if "sustained" in ttl:
            pk = [i for i in range(1, len(y) - 1) if y[i] > y[i - 1] and y[i] > y[i + 1]][1:3]
            ax.annotate("", xy=(t[pk[1]], 2.3), xytext=(t[pk[0]], 2.3), arrowprops=dict(arrowstyle="<->", color=RED))
            ax.text((t[pk[0]] + t[pk[1]]) / 2, 2.38, rf"$T_u={TU:.2f}$", color=RED, ha="center", va="bottom")
    for a in axs[1]: a.set_xlabel("time")
    fig.suptitle(rf"Van de Vusse reactor under P control: $K_{{cu}}={KCU:.3f}$", y=1.01)
    fig.tight_layout(); fig.savefig(OUT / "f02_ultimate_cycle.png"); plt.close(fig)


def fig_vdv():
    t = np.linspace(0, 5, 5001)
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.3))
    a = axs[0]
    for (nm, C), c in zip([("P  $0.5K_{cu}$", pid_tf(0.5 * KCU)),
                           ("PI  $0.455K_{cu},\\ 0.833T_u$", pid_tf(0.455 * KCU, 0.833 * TU)),
                           ("PID  $0.6K_{cu},\\ 0.5T_u,\\ 0.125T_u$", pid_tf(0.6 * KCU, 0.5 * TU, 0.125 * TU))], COL):
        T = ct.feedback(C * GVV, 1); a.plot(t, y_(T, t), color=c, lw=2, label=nm)
    a.axhline(1, color=GRAY, ls=":"); a.axhline(0.5 * KCU * 0.5858 / (1 + 0.5 * KCU * 0.5858), color=NAVY, ls=":", lw=1)
    a.text(4.2, 0.59, "P offset", color=NAVY, fontsize=10)
    a.set_title("ZN quarter-decay settings"); a.legend(loc="lower right", fontsize=10); a.set_xlabel("time"); a.set_ylabel(r"$C(t)$")
    a = axs[1]
    for (nm, k, d), c in zip([("quarter decay", 0.6, 0.125), ("some overshoot", 0.33, 1 / 3), ("no overshoot", 0.2, 1 / 3)], COL):
        T = ct.feedback(pid_tf(k * KCU, 0.5 * TU, d * TU) * GVV, 1); a.plot(t, y_(T, t), color=c, lw=2, label=f"PID, {nm}")
    a.axhline(1, color=GRAY, ls=":"); a.set_title("three ZN PID variants"); a.legend(loc="lower right", fontsize=10); a.set_xlabel("time")
    for a in axs: a.set_ylim(-1, 1.5)
    fig.tight_layout(); fig.savefig(OUT / "f03_vdv_zn.png"); plt.close(fig)


def fig_integrals():
    t = np.linspace(0, 12, 3000)
    T = ct.feedback(pid_tf(2.03, 3.76) * GT, 1); e = 1 - y_(T, t)
    fig, axs = plt.subplots(1, 3, figsize=(14, 3.6), sharex=True)
    for a, (w, ttl, c) in zip(axs, [(e ** 2, r"ISE: $e^2$", NAVY), (abs(e), r"IAE: $|e|$", GREEN), (t * abs(e), r"ITAE: $t\,|e|$", RED)]):
        a.fill_between(t, w, color=c, alpha=0.25); a.plot(t, w, color=c, lw=1.8)
        a.set_title(ttl + f"   (area {np.trapezoid(w, t):.2f})"); a.set_xlabel("time")
    axs[0].set_ylabel("integrand")
    fig.suptitle("Same response, three weightings: ITAE punishes errors that persist", y=1.04)
    fig.tight_layout(); fig.savefig(OUT / "f04_error_integrals.png"); plt.close(fig)


def fig_compare():
    t0 = np.linspace(0, 30, 30001); K, tau, th = fit_two_point(t0, y_(GT, t0))
    t = np.linspace(0, 25, 5001)
    fig, axs = plt.subplots(2, 2, figsize=(13, 7), sharex=True)
    names = ["Ziegler–Nichols (PRC)", "Cohen–Coon", "ITAE set point", "ITAE load", "IMC (τc = θ)"]
    for col, ctrl in enumerate(("PI", "PID")):
        for nm, c in zip(names, COL):
            C = pid_tf(*RULES[nm](ctrl, K, tau, th))
            axs[0, col].plot(t, y_(ct.feedback(C * GT, 1), t), color=c, lw=1.9, label=nm.replace("τc", r"$\tau_c$").replace("θ", r"$\theta$"))
            axs[1, col].plot(t, y_(ct.feedback(GT, C), t), color=c, lw=1.9)
        axs[0, col].set_title(f"{ctrl}: set-point step"); axs[1, col].set_title(f"{ctrl}: load step at the process input")
        axs[0, col].axhline(1, color=GRAY, ls=":"); axs[1, col].axhline(0, color=GRAY, ls=":"); axs[1, col].set_xlabel("time")
    axs[0, 0].legend(loc="lower right", fontsize=9.5); axs[0, 0].set_ylabel(r"$C(t)$"); axs[1, 0].set_ylabel(r"$C(t)$")
    fig.tight_layout(); fig.savefig(OUT / "f05_rule_comparison.png"); plt.close(fig)


def fig_imc():
    t0 = np.linspace(0, 30, 30001); K, tau, th = fit_two_point(t0, y_(GT, t0))
    t = np.linspace(0, 20, 4001)
    fig, ax = plt.subplots(figsize=(8, 4.3))
    for f, c in zip((0.5, 1.0, 2.0), COL):
        pars = imc("PID", K, tau, th, f * th)
        ax.plot(t, y_(ct.feedback(pid_tf(*pars) * GT, 1), t), color=c, lw=2, label=rf"$\tau_c={f}\theta$  ($K_c={pars[0]:.2f}$)")
    ax.axhline(1, color=GRAY, ls=":"); ax.legend(loc="lower right", fontsize=10.5)
    ax.set_title(r"IMC-PID on the Ex 3.6 plant: one knob, $\tau_c$"); ax.set_xlabel("time"); ax.set_ylabel(r"$C(t)$")
    fig.tight_layout(); fig.savefig(OUT / "f06_imc_tauc.png"); plt.close(fig)
    t = np.linspace(0, 5, 5001)
    fig, ax = plt.subplots(figsize=(8, 4.3))
    for tc, c in zip((0.15, 0.3), (NAVY, GREEN)):
        ax.plot(t, y_(ct.tf([-0.3549, 1], np.polymul([tc, 1], [tc, 1])), t), color=c, lw=2, label=rf"IMC, $\tau_c={tc}$")
    ax.plot(t, y_(ct.feedback(pid_tf(0.6 * KCU, 0.5 * TU, 0.125 * TU) * GVV, 1), t), color=RED, lw=1.6, ls="--", label="ZN PID (quarter decay)")
    ax.axhline(1, color=GRAY, ls=":"); ax.set_ylim(-1, 1.5); ax.legend(loc="lower right", fontsize=10.5)
    ax.set_title(r"Van de Vusse: $C/R=(-0.3549s+1)/(\tau_cs+1)^2$"); ax.set_xlabel("time"); ax.set_ylabel(r"$C(t)$")
    fig.tight_layout(); fig.savefig(OUT / "f08_imc_vdv.png"); plt.close(fig)



def save_(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name); plt.close(fig)


# ---------------------------------------------------------------- relay autotuning
def fig_relay():
    t, y, u = simulate(GT, 0, relay_law(1.0), 25, r=lambda t: 0.1)
    m = t > 12; a = (y[m].max() - y[m].min()) / 2
    sw = t[m][np.where(np.diff(u[m]) != 0)[0]]; P = 2 * np.mean(np.diff(sw))
    Kcu, _, wc, _ = ct.margin(GT)
    fig, ax = plt.subplots(figsize=(11.5, 3.2))
    ax.plot(t, u, color=RED, lw=1.6, label=r"relay output $p$ ($\pm h$, $h=1$)")
    ax.plot(t, 5 * y, color=NAVY, lw=2.4, label=r"measured output $\times5$")
    ax.axhline(0, color="k", lw=0.6)
    i0 = np.argmax((t > 15) & (np.r_[False, np.diff(np.sign(np.diff(y))) < 0, False]))
    ax.annotate("", xy=(t[i0], 5 * y.max()), xytext=(t[i0], 5 * y[m].min()), arrowprops=dict(arrowstyle="<->", color=NAVY))
    ax.text(t[i0] + 0.2, 0.0, r"$2a$", color=NAVY, fontsize=14)
    ax.annotate("", xy=(sw[2] + P, 1.25), xytext=(sw[2], 1.25), arrowprops=dict(arrowstyle="<->", color=RED))
    ax.text(sw[2] + P / 2, 1.33, r"$P_u$", color=RED, fontsize=14, ha="center")
    ax.set_ylim(-1.5, 1.6); ax.set_xlabel("time"); ax.legend(fontsize=10.5, loc="lower right", ncol=2)
    ax.set_title(rf"Relay test on $1/[(2s+1)(s+1)(0.5s+1)]$: $K_{{cu}}\approx4h/(\pi a)={4 / (np.pi * a):.2f}$ "
                 rf"(exact {Kcu:.2f}), $P_u={P:.2f}$ (exact {2 * np.pi / wc:.2f})")
    save_(fig, "f09_relay.png")


def fig_simc():
    s_ = ct.tf("s"); G = 1 / (20 * s_ + 1); th = 1.0
    sets = [("IMC  ($\\tau_I=\\tau=20$)", (10.0, 20.0), NAVY), ("SIMC ($\\tau_I=4(\\tau_c+\\theta)=8$)", simc("PI", 1, 20, 1)[:2], RED)]
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.9))
    for lab, (Kc, tI), c in sets:
        t, y, _ = simulate(G, th, pi_law(Kc, tI), 25)
        axs[0].plot(t, y, color=c, lw=2.2, label=lab)
        t, y, _ = simulate(G, th, pi_law(Kc, tI), 60, r=lambda t: 0.0, load=lambda t: 1.0)
        axs[1].plot(t, y, color=c, lw=2.2, label=f"{lab}: IAE {np.trapezoid(abs(y), t):.2f}")
    axs[0].axhline(1, color=GRAY, ls=":"); axs[1].axhline(0, color=GRAY, lw=0.6)
    axs[0].set_title(r"set-point step ($K_c=10$ in both)"); axs[1].set_title("unit load step at the process input")
    for a in axs: a.set_xlabel("time"); a.legend(fontsize=10, loc="lower right" if a is axs[0] else "upper right")
    fig.suptitle(r"Lag-dominant process $e^{-s}/(20s+1)$, $\tau_c=\theta=1$", y=1.02)
    save_(fig, "f10_simc_lag.png")


def fig_integrating():
    s_ = ct.tf("s"); G = 0.2 / s_; th = 1.0
    Kc, tI = simc_integrating(0.2, th)
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    for lab, law, c in ((rf"SIMC PI: $K_c={Kc:.1f},\ \tau_I={tI:.0f}$", pi_law(Kc, tI), NAVY),
                        (r"$\tau_I=2$ (too much integral action)", pi_law(Kc, 2.0), RED),
                        (r"P only ($\tau_I\to\infty$)", lambda e, dt: Kc * e, GREEN)):
        t, y, _ = simulate(G, th, law, 70, load=lambda t: -0.5 if t >= 35 else 0.0)
        ax.plot(t, y, color=c, lw=2.2, label=lab)
    ax.axhline(1, color=GRAY, ls=":"); ax.axvline(35, color=GRAY, ls="--", lw=1)
    ax.text(35.5, 0.12, "load step $-0.5$", color=GRAY)
    ax.text(50, 0.68, r"P only: offset $=0.5/K_c=0.2$", color=GREEN)
    ax.set_xlabel("time"); ax.set_ylim(0, 2.0); ax.legend(fontsize=10.5, loc="upper right")
    ax.set_title(r"$0.2e^{-s}/s$: set-point step at 0, load step at 35")
    save_(fig, "f11_integrating.png")

if __name__ == "__main__":
    for f in (fig_prc, fig_ultimate, fig_vdv, fig_integrals, fig_compare, fig_imc, fig_relay, fig_simc, fig_integrating):
        f(); print("ok", f.__name__)
    print("VdV Kcu", KCU, "Tu", TU)
