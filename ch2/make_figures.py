"""Figures for Ch.2 Analysis of Single-Loop Control Systems."""
import numpy as np
import matplotlib.pyplot as plt
import control as ct
from pathlib import Path

OUT = Path(__file__).parent / "figures"; OUT.mkdir(exist_ok=True)
NAVY, RED, GREEN, ORANGE, GRAY, PURPLE = "#333399", "#C00000", "#2E7D32", "#E07B00", "#888888", "#7b1fa2"
COL = [GRAY, NAVY, RED, GREEN, ORANGE, PURPLE]
plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150, "savefig.bbox": "tight",
                     "mathtext.fontset": "cm", "axes.grid": True, "grid.color": "#e3e3e3", "grid.linewidth": 0.6})

y_ = lambda sysm, t: np.asarray(ct.step_response(sysm, t).outputs, float).ravel()
G3 = ct.tf(1, [1, 3, 3, 1])                       # 1/(s+1)^3, load enters with the manipulated input


def pid(Kc, tI=None, tD=0.0, alpha=0.1):
    C = ct.tf(Kc, 1)
    if tI: C = C + ct.tf(Kc, [tI, 0])
    if tD: C = C + ct.tf([Kc * tD, 0], [alpha * tD, 1])
    return C


def load(C, G=G3):                                 # C/L with G_L = G_p
    return ct.feedback(G, C)


def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name); plt.close(fig)


# ---------------------------------------------------------------- 2.1 hardware
def fig_valve():
    l = np.linspace(0, 1, 201)
    fig, ax = plt.subplots(figsize=(5.4, 4.4))
    ax.plot(l, np.sqrt(l), color=RED, lw=2.4, label=r"quick opening  $f=\sqrt{\ell}$")
    ax.plot(l, l, color=NAVY, lw=2.4, label=r"linear  $f=\ell$")
    ax.plot(l, 40.0 ** (l - 1), color=GREEN, lw=2.4, label=r"equal percentage  $f=R^{\,\ell-1},\ R=40$")
    ax.set_xlabel(r"lift  $\ell$"); ax.set_ylabel(r"flow fraction  $f(\ell)$"); ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.legend(loc="upper left", fontsize=10); ax.set_title("Inherent valve characteristics")
    save(fig, "f01_valve.png")


def fig_heater():
    """Heater loop of 2.1.4 under P control: Gp=0.85/(20s+1), Gv=0.6/(0.2s+1), Km=0.16 mA/degC."""
    Gp, Gv, Km = ct.tf(0.85, [20, 1]), ct.tf(0.6, [0.2, 1]), 0.16
    t = np.linspace(0, 60, 3001)
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    for Kc, c in zip((5, 10, 20, 50), COL[1:]):
        T = ct.feedback(Km * Kc * Gv * Gp, 1)
        K = Kc * 0.6 * 0.85 * 0.16
        ax.plot(t, y_(T, t), color=c, lw=2.2, label=rf"$K_c={Kc}$:  $K_{{OL}}={K:.2f}$, offset {1 / (1 + K):.0%}")
    ax.axhline(1, color=GRAY, ls=":"); ax.set_ylim(0, 1.75); ax.set_xlim(0, 60)
    ax.set_xlabel("time (min)"); ax.set_ylabel(r"$T'/T'_{sp}$"); ax.legend(loc="upper center", fontsize=10.5, ncol=1, bbox_to_anchor=(0.5, 1.02))
    ax.set_title("Heater loop, P control: 1 °C set-point step")
    save(fig, "f02_heater.png")


# ---------------------------------------------------------------- 2.2 PID modes
def fig_p():
    t = np.linspace(0, 20, 4001)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.0), gridspec_kw={"width_ratios": [1.5, 1]})
    a = axs[0]
    for Kc, c in zip((0, 1, 3, 6), COL):
        lab = "no control ($K_c=0$)" if Kc == 0 else rf"$K_c={Kc}$, offset $={1 / (1 + Kc):.2f}$"
        a.plot(t, y_(load(pid(Kc) if Kc else ct.tf(0, 1)), t), color=c, lw=2.2, label=lab)
    a.set_xlabel("time"); a.set_ylabel(r"$C$  (unit load step)"); a.legend(fontsize=10, loc="upper right")
    a.set_title(r"P control of $1/(s+1)^3$: faster, smaller offset, more oscillatory"); a.set_ylim(-0.05, 1.25)
    a = axs[1]; e = np.linspace(-1.5, 1.5, 301); Kc = 2
    a.plot(e, 0.5 + 0.2 * Kc * e, color=GRAY, lw=1.4, ls="--", label="ideal")
    a.plot(e, np.clip(0.5 + 0.2 * Kc * e, 0.1, 0.9), color=NAVY, lw=2.4, label="real (saturates)")
    a.axhline(0.9, color=RED, ls=":", lw=1); a.axhline(0.1, color=RED, ls=":", lw=1)
    a.text(-1.45, 0.93, r"$p_{\max}$", color=RED); a.text(-1.45, 0.13, r"$p_{\min}$", color=RED)
    a.plot(0, 0.5, "o", color=NAVY); a.text(0.08, 0.44, r"$p^s$ (bias)", color=NAVY)
    a.set_xlabel(r"error $e$"); a.set_ylabel(r"controller output $p$"); a.set_ylim(-0.05, 1.12)
    a.legend(fontsize=10, loc="lower right", bbox_to_anchor=(1, 0.08)); a.set_title(r"$p=p^s+K_c e$ with saturation")
    save(fig, "f03_p_control.png")


def fig_pi_windup():
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.0), gridspec_kw={"width_ratios": [1, 1.5]})
    a = axs[0]; t = np.linspace(-1, 4, 501); Kc, tI = 1, 2
    a.plot(t, np.where(t < 0, 0, 1), color=GRAY, lw=2, ls="--", label="error $e$ (unit step)")
    a.plot(t, np.where(t < 0, 0, Kc + Kc / tI * t), color=NAVY, lw=2.4, label=r"PI output $p-p^s$")
    a.annotate("", xy=(0.05, Kc), xytext=(0.05, 0), arrowprops=dict(arrowstyle="<->", color=RED))
    a.text(0.15, 0.45, r"$K_c$", color=RED, fontsize=14); a.text(2.2, 2.3, r"slope $=K_c/\tau_I$", color=RED, fontsize=13)
    a.set_xlabel("time"); a.legend(fontsize=10, loc="upper left"); a.set_title(r"PI response to a step in $e$"); a.set_ylim(-0.2, 3.4)
    # windup: PI on 1/(s+1)^3 with output limits, large set-point step
    a = axs[1]; dt, T = 0.002, 40; n = int(T / dt); Kc, tI, umax = 2.5, 2.0, 1.25
    A, B, Cm, _ = (np.asarray(m) for m in ct.ssdata(ct.tf2ss(G3))); B = B.ravel(); Cm = Cm.ravel()
    for aw, c, lab in ((False, RED, "no anti-windup"), (True, NAVY, "anti-windup (clamping)")):
        x = np.zeros(3); I = 0.0; ys = np.zeros(n); us = np.zeros(n)
        for k in range(n):
            yk = Cm @ x; e = 1 - yk
            v = Kc * (e + I / tI); u = np.clip(v, -umax, umax)
            if not aw or v == u or np.sign(e) != np.sign(v):
                I += e * dt
            x = x + dt * (A @ x + B * u); ys[k], us[k] = yk, u
        tt = np.arange(n) * dt
        a.plot(tt, ys, color=c, lw=2.4, label=lab); a.plot(tt, us, color=c, lw=1, ls=":")
    a.axhline(1, color=GRAY, ls="--", lw=1); a.axhline(umax, color=GRAY, lw=0.8)
    a.text(32, umax + 0.04, r"$p_{\max}$", color=GRAY)
    a.set_xlabel("time"); a.set_ylabel(r"$C$ (solid), $p$ (dotted)"); a.legend(fontsize=10, loc="lower right")
    a.set_title("Reset windup: the integral keeps growing while the valve is saturated"); a.set_ylim(-0.1, 1.7)
    save(fig, "f04_pi_windup.png")


def fig_pi_tune():
    t = np.linspace(0, 30, 3001)
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.9), sharey=True)
    for tI, c in zip((1.5, 3, 8), COL[1:]):
        axs[0].plot(t, y_(load(pid(2, tI)), t), color=c, lw=2.2, label=rf"$\tau_I={tI}$")
    axs[0].set_title(r"(a) $K_c=2$: smaller $\tau_I$ (more I) $\to$ more oscillatory")
    for Kc, c in zip((1, 2, 3.5), COL[1:]):
        axs[1].plot(t, y_(load(pid(Kc, 3)), t), color=c, lw=2.2, label=rf"$K_c={Kc}$")
    axs[1].set_title(r"(b) $\tau_I=3$: larger $K_c$ $\to$ smaller peak, more oscillatory")
    for a in axs:
        a.axhline(0, color=GRAY, lw=0.8); a.set_xlabel("time"); a.legend(fontsize=10)
    axs[0].set_ylabel(r"$C$  (unit load step)")
    save(fig, "f05_pi_tuning.png")


def fig_kick():
    """Set-point step: derivative on the error (kick) versus on the measurement."""
    dt, T = 0.001, 12; n = int(T / dt); Kc, tI, tD, al = 2.5, 2.5, 0.6, 0.1
    A, B, Cm, _ = (np.asarray(m) for m in ct.ssdata(ct.tf2ss(G3))); B = B.ravel(); Cm = Cm.ravel()
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.9))
    for onmeas, c, lab in ((False, RED, "D on error"), (True, NAVY, "D on measurement")):
        x = np.zeros(3); I = 0.0; df = 0.0; prev = 0.0; ys, us = np.zeros(n), np.zeros(n)
        for k in range(n):
            r = 1.0 if k * dt >= 1 else 0.0; yk = Cm @ x; e = r - yk; I += e * dt
            sig = -yk if onmeas else e
            df += dt * (tD * (sig - prev) / dt - df) / (al * tD); prev = sig
            u = Kc * (e + I / tI + df); x = x + dt * (A @ x + B * u); ys[k], us[k] = yk, u
        tt = np.arange(n) * dt
        axs[0].plot(tt, ys, color=c, lw=2.2, label=lab); axs[1].plot(tt, us, color=c, lw=2, label=lab)
    axs[0].set_title("controlled variable"); axs[1].set_title("controller output: the derivative kick")
    axs[1].set_ylim(-2, 30)
    axs[1].annotate(r"spike $\approx K_c/\alpha$", xy=(1.02, 26), xytext=(3, 24), color=RED,
                    arrowprops=dict(arrowstyle="->", color=RED))
    for a in axs: a.set_xlabel("time"); a.legend(fontsize=10, loc="center right")
    save(fig, "f06_kick.png")


def fig_modes():
    t = np.linspace(0, 25, 3001)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for (lab, C), c in zip([("no control", None), ("P  ($K_c=2$)", pid(2)), ("PI  ($K_c=2,\\ \\tau_I=2.5$)", pid(2, 2.5)),
                            ("PID  ($K_c=3,\\ \\tau_I=2,\\ \\tau_D=0.6$)", pid(3, 2, 0.6))], COL):
        ax.plot(t, y_(G3 if C is None else load(C), t), color=c, lw=2.4, label=lab)
    ax.axhline(0, color=GRAY, lw=0.8); ax.set_xlabel("time"); ax.set_ylabel(r"$C$  (unit load step)")
    ax.legend(fontsize=10.5); ax.set_title(r"Load response of $1/(s+1)^3$ under each mode")
    save(fig, "f07_modes.png")


# ---------------------------------------------------------------- 2.3 examples
def fig_examples():
    plt.rcParams.update({"font.size": 13})
    fig, axs = plt.subplots(2, 2, figsize=(9.6, 7.2))
    t = np.linspace(0, 10, 2001)
    a = axs[0, 0]; Gp = ct.tf(1, [2, 1])
    for Kc, c in zip((0.5, 2, 8), COL[1:]):
        a.plot(t, y_(ct.feedback(Kc * Gp, 1), t), color=c, lw=2.2, label=rf"$K_cK_p={Kc}$, $\tau_{{cl}}={2 / (1 + Kc):.2f}$")
        a.axhline(Kc / (1 + Kc), color=c, ls=":", lw=1)
    a.set_title(r"Ex 2.1  P + first order ($\tau_p=2$)"); a.legend(fontsize=11.5, loc="center right", bbox_to_anchor=(1, 0.42)); a.set_ylim(0, 1.1)
    a = axs[0, 1]; G2 = ct.tf(1, [8, 6, 1]); t2 = np.linspace(0, 30, 3001)
    for Kc, c in zip((0.3, 1.296, 5), COL[1:]):
        T = ct.feedback(Kc * G2, 1); z = 3 / np.sqrt(8 * (1 + Kc))
        a.plot(t2, y_(T, t2), color=c, lw=2.2, label=rf"$K_c={Kc}$, $\zeta={z:.2f}$")
    a.set_title(r"Ex 2.2  P + $1/[(2s+1)(4s+1)]$"); a.legend(fontsize=11.5, loc="lower right"); a.set_ylim(0, 1.1)
    a = axs[1, 0]; Gp = ct.tf(1, [2, 1])
    for tI, c in zip((0.2, 0.6, 2), COL[1:]):
        T = ct.feedback(pid(1, tI) * Gp, 1); z = 0.5 * 2 * np.sqrt(tI / (1 * 2))
        a.plot(t, y_(T, t), color=c, lw=2.2, label=rf"$K_cK_p=1$, $\tau_I={tI}$, $\zeta={z:.2f}$")
    a.axhline(1, color=GRAY, ls=":"); a.set_title(r"Ex 2.3  PI + first order: no offset"); a.legend(fontsize=11.5, loc="lower right")
    a = axs[1, 1]; Gi = ct.tf(1, [1, 0]); Kc = 0.8; t4 = np.linspace(0, 12, 2001)
    a.plot(t4, y_(ct.feedback(Kc * Gi, 1), t4), color=NAVY, lw=2.2, label=r"set-point step: $C\to1$")
    a.plot(t4, y_(ct.feedback(Gi, Kc), t4), color=RED, lw=2.2, label=rf"load step (at input): $C\to1/K_c={1 / Kc:.2f}$")
    a.plot(t4, y_(ct.feedback(Gi, pid(Kc, 2)), t4), color=GREEN, lw=2.2, label=r"load step with PI: $C\to0$")
    a.set_title(r"Ex 2.5  P + integrating process $1/s$ ($K_c=0.8$)"); a.legend(fontsize=11.5, loc="upper right")
    a.set_ylim(-0.2, 2.0)
    for a in axs.ravel(): a.set_xlabel("time")
    save(fig, "f08_examples.png"); plt.rcParams.update({"font.size": 12})


def fig_ex26():
    Gp = ct.tf(0.8, [5, 1]); t = np.linspace(0, 6, 3001)
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ax.plot(t, y_(ct.feedback(10 * Gp, 1), t), color=NAVY, lw=2.4, label=r"P:  $G_c=10$")
    ax.plot(t, y_(ct.feedback(pid(10, 1) * Gp, 1), t), color=RED, lw=2.4, label=r"PI:  $G_c=10(1+1/s)$")
    ax.axhline(8 / 9, color=NAVY, ls=":", lw=1); ax.axhline(1, color=GRAY, ls=":", lw=1)
    ax.text(4.6, 0.80, r"$K_{cl}=8/9$", color=NAVY)
    ax.set_xlabel("time"); ax.set_ylabel(r"$C$"); ax.legend(loc="lower right"); ax.set_ylim(0, 1.25)
    ax.set_title(r"Example 2.6:  $G_p=0.8/(5s+1)$, unit set-point step")
    save(fig, "f09_ex26.png")


if __name__ == "__main__":
    for f in (fig_valve, fig_heater, fig_p, fig_pi_windup, fig_pi_tune, fig_kick, fig_modes, fig_examples, fig_ex26):
        f()
    print(sorted(p.name for p in OUT.glob("*.png")))
