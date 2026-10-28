"""Figures for Ch.1 Mathematical Preliminaries and Dynamic Response."""
import numpy as np
import matplotlib.pyplot as plt
import control as ct
from pathlib import Path

OUT = Path(__file__).parent / "figures"; OUT.mkdir(exist_ok=True)
NAVY, RED, GREEN, ORANGE, GRAY, PURPLE = "#333399", "#C00000", "#2E7D32", "#E07B00", "#888888", "#7b1fa2"
COL = [NAVY, RED, GREEN, ORANGE, PURPLE]
plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150, "savefig.bbox": "tight",
                     "mathtext.fontset": "cm", "axes.grid": True, "grid.color": "#e3e3e3", "grid.linewidth": 0.6})

step = lambda G, t: np.asarray(ct.step_response(G, t).outputs, float).ravel()
imp = lambda G, t: np.asarray(ct.impulse_response(G, t).outputs, float).ravel()


def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name); plt.close(fig)


def delayed(y, t, th):
    """Shift a response sampled on t by a dead time th."""
    return np.interp(t - th, t, y, left=0.0)


# ---------------------------------------------------------------- 1.1 models
def fig_linearize():
    beta, hs = 1.0, 4.0
    h = np.linspace(0, 10, 400)
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    ax.plot(h, beta * np.sqrt(h), color=NAVY, lw=2.6, label=r"$q=\beta\sqrt{h}$")
    ax.plot(h, beta * np.sqrt(hs) + beta / (2 * np.sqrt(hs)) * (h - hs), color=RED, lw=2, ls="--",
            label=r"tangent at $h_s$:  $\beta\sqrt{h_s}+\dfrac{\beta}{2\sqrt{h_s}}(h-h_s)$")
    ax.plot(hs, np.sqrt(hs), "o", color=RED, ms=7)
    ax.axvspan(hs - 1.5, hs + 1.5, color=GREEN, alpha=0.08); ax.text(hs, 0.25, "good near $h_s$", color=GREEN, ha="center")
    ax.set_xlabel("$h$"); ax.set_ylabel("$q$"); ax.set_xlim(0, 10); ax.set_ylim(0, 3.6)
    ax.legend(fontsize=10.5, loc="upper left"); ax.set_title("Linearization: first-order Taylor expansion")
    save(fig, "f01_linearize.png")


# ---------------------------------------------------------------- 1.2 inputs
def fig_inputs():
    t = np.linspace(-0.5, 3, 800)
    fig, axs = plt.subplots(1, 4, figsize=(13, 2.9), sharey=True)
    cfg = [("unit step  $u(t)$", np.where(t >= 0, 1, 0), r"$1/s$"),
           ("dead time  $f(t-t_0)u(t-t_0)$", np.where(t >= 1, 1 - np.exp(-(t - 1) / 0.6), 0), r"$e^{-t_0 s}F(s)$"),
           ("rectangular pulse", np.where((t >= 0) & (t < 1.2), 1, 0), r"$\dfrac{A}{s}\left(1-e^{-Ts}\right)$"),
           ("unit impulse  $\\delta(t)$", None, r"$1$")]
    for a, (ttl, y, F) in zip(axs, cfg):
        if y is None:
            a.annotate("", xy=(0, 1.15), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2.6))
            a.plot([-0.5, 3], [0, 0], color=NAVY, lw=2.6); a.text(0.15, 0.9, "area = 1", color=NAVY)
        else:
            a.plot(t, y, color=NAVY, lw=2.6)
        if "dead" in ttl:
            a.plot(t, np.where(t >= 0, 1 - np.exp(-t / 0.6), 0), color=GRAY, lw=1.4, ls="--")
            a.annotate("", xy=(1, 0.08), xytext=(0, 0.08), arrowprops=dict(arrowstyle="<->", color=RED))
            a.text(0.5, 0.14, "$t_0$", color=RED, ha="center")
        if ttl.startswith("rect"):
            a.text(0.6, 1.05, "$A$", color=NAVY, ha="center"); a.text(1.2, -0.12, "$T$", color=NAVY, ha="center")
        a.set_title(ttl, fontsize=12); a.text(2.95, 0.5, F, color=RED, ha="right", fontsize=15)
        a.set_ylim(-0.2, 1.3); a.set_xlabel("$t$")
    save(fig, "f02_inputs.png")


def fig_terms():
    t = np.linspace(0, 1.5, 400)
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    for y, lab, c in [(2 * np.exp(-t), r"$2e^{-t}$", NAVY), (3 * np.exp(-2 * t), r"$3e^{-2t}$", GREEN),
                      (np.exp(2 * t), r"$e^{2t}$  (pole at $+2$)", RED)]:
        ax.plot(t, y, color=c, lw=2.2, label=lab)
    ax.set_xlabel("$t$"); ax.legend(fontsize=11); ax.set_title("Ex 1.5: the three terms of $f(t)$")
    save(fig, "f03_terms.png")


# ---------------------------------------------------------------- 1.4 poles
def fig_poles():
    import matplotlib.gridspec as gs
    cases = [("A", -0.5, 0, NAVY), ("B", -2, 0, GREEN), ("C", -0.5, 2.5, ORANGE),
             ("D", 0, 2.5, PURPLE), ("E", 0.15, 2.5, RED), ("F", 0.2, 0, RED)]
    fig = plt.figure(figsize=(13, 5.0)); g = gs.GridSpec(2, 5, figure=fig, width_ratios=[1.6, 1, 1, 1, 0.01])
    ax = fig.add_subplot(g[:, 0])
    ax.axvspan(0, 1, color=RED, alpha=0.07); ax.text(0.5, 3.4, "unstable", color=RED, ha="center")
    ax.text(-1.6, 3.4, "stable (LHP)", color=GREEN, ha="center")
    ax.axhline(0, color="k", lw=0.8); ax.axvline(0, color="k", lw=0.8)
    for lab, re, im, c in cases:
        for sg in ((1, -1) if im else (1,)):
            ax.plot(re, sg * im, "x", color=c, ms=11, mew=2.6)
        ax.text(re + 0.08, im + 0.25, lab, color=c, fontsize=14, weight="bold")
    ax.set_xlim(-2.6, 1); ax.set_ylim(-3.8, 3.8); ax.set_xlabel("Re $s$"); ax.set_ylabel("Im $s$")
    ax.set_title("pole locations"); ax.set_aspect("auto")
    t = np.linspace(0, 10, 1000)
    for k, (lab, re, im, c) in enumerate(cases):
        a = fig.add_subplot(g[k // 3, 1 + k % 3])
        y = np.exp(re * t) * (np.cos(im * t) if im else 1)
        a.plot(t, y, color=c, lw=2.2); a.axhline(0, color="k", lw=0.6)
        nm = f"${re:g}$" if not im else f"${re:g}\\pm{im:g}j$"
        a.set_title(f"{lab}:  {nm}", fontsize=12, color=c); a.set_ylim(-2.2, 2.2); a.set_yticks([]); a.set_xticks([0, 5, 10])
    fig.suptitle("Each pole contributes a term $e^{pt}$: the real part sets decay or growth, the imaginary part the oscillation",
                 fontsize=13, y=1.02)
    save(fig, "f04_poles.png")


# ---------------------------------------------------------------- 1.5 first order
def fig_first_order():
    t = np.linspace(0, 12, 1201)
    fig, axs = plt.subplots(2, 2, figsize=(11.5, 6.4), sharex=True)
    for tau, c in zip((2, 1, 0.5, 0.25), COL):
        G = ct.tf(1, [tau, 1])
        axs[0, 0].plot(t, step(G, t), color=c, lw=2.2, label=rf"$\tau={tau}$ (pole $-{1 / tau:g}$)")
        axs[1, 0].plot(t, imp(G, t), color=c, lw=2.2, label=rf"$\tau={tau}$")
    for K, c in zip((0.5, 1, 1.5, 2), COL):
        G = ct.tf(K, [1, 1])
        axs[0, 1].plot(t, step(G, t), color=c, lw=2.2, label=rf"$K={K}$")
        axs[1, 1].plot(t, imp(G, t), color=c, lw=2.2, label=rf"$K={K}$")
    axs[0, 0].plot([2, 2, 0], [0, 0.632, 0.632], color=NAVY, ls=":", lw=1.2)
    axs[0, 0].text(2.15, 0.56, r"63.2% at $t=\tau$", color=NAVY, fontsize=11)
    axs[0, 0].set_title(r"step, $K=1$: larger $\tau$ is slower"); axs[0, 1].set_title(r"step, $\tau=1$: $y(\infty)=KM$")
    axs[1, 0].set_title(r"impulse: $y(0^+)=KM/\tau$"); axs[1, 1].set_title(r"impulse, $\tau=1$")
    for a in axs.ravel(): a.legend(fontsize=10, loc="center right")
    for a in axs[1]: a.set_xlabel("$t$")
    axs[0, 0].set_ylabel("$y$ (unit step)"); axs[1, 0].set_ylabel("$y$ (unit impulse)")
    save(fig, "f05_first_order.png")


def fig_ramp():
    tau, t = 1.0, np.linspace(0, 5, 500)
    y = tau * (np.exp(-t / tau) - 1) + t
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    ax.plot(t, t, color=GRAY, lw=2, label=r"input $x/a=t$")
    ax.plot(t, y, color=NAVY, lw=2.6, label=r"output $y/(Ka)$")
    ax.plot(t, t - tau, color=RED, ls="--", lw=1.4, label=r"asymptote $t-\tau$")
    ax.annotate("", xy=(4.0, 3.0), xytext=(3.0, 3.0), arrowprops=dict(arrowstyle="<->", color=RED))
    ax.text(3.5, 3.12, r"lag $\tau$", color=RED, ha="center")
    ax.set_xlabel(r"$t/\tau$"); ax.legend(fontsize=10.5, loc="upper left"); ax.set_title("Ramp response of a first-order model")
    save(fig, "f06_ramp.png")


def fig_two_tanks():
    t = np.linspace(0, 15, 15001); G1, G2 = ct.tf(1, [2, 1]), ct.tf(1, [1.5, 1])
    u = np.where(t < 0.25, 5.0, 0.0)
    c1 = ct.forced_response(G1, t, u).outputs + 1; c2 = ct.forced_response(G1 * G2, t, u).outputs + 1
    i1 = 1.25 * imp(G1, t) + 1; i2 = 1.25 * imp(G1 * G2, t) + 1
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    ax.plot(t, c1, color=NAVY, lw=2.4, label="$c_1$, pulse"); ax.plot(t, i1, color=NAVY, lw=1.4, ls="--", label=r"$c_1$, impulse $1.25\delta(t)$")
    ax.plot(t, c2, color=RED, lw=2.4, label="$c_2$, pulse"); ax.plot(t, i2, color=RED, lw=1.4, ls="--", label=r"$c_2$, impulse")
    ax.set_xlabel("time (min)"); ax.set_ylabel(r"concentration (kmol/m$^3$)"); ax.legend(fontsize=10.5)
    ax.set_title(r"Ex 1.8: a 0.25-min pulse of height 5 is almost an impulse of area 1.25")
    save(fig, "f07_two_tanks.png")


# ---------------------------------------------------------------- 1.6 second order
def fig_second_order():
    t = np.linspace(0, 20, 2001)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.0), sharey=True)
    for z, c in zip((1, 1.5, 2, 3), COL):
        axs[0].plot(t, step(ct.tf(1, [1, 2 * z, 1]), t), color=c, lw=2.2, label=rf"$\zeta={z}$")
    for z, c in zip((0.2, 0.4, 0.6, 0.8, 0), COL):
        axs[1].plot(t, step(ct.tf(1, [1, 2 * z, 1]), t), color=c, lw=2.2 if z else 1.2, ls="-" if z else ":",
                    label=rf"$\zeta={z}$" + (" (undamped)" if z == 0 else ""))
    axs[0].set_title(r"$\zeta\geq1$: overdamped / critically damped"); axs[1].set_title(r"$0\leq\zeta<1$: underdamped")
    for a in axs: a.set_xlabel(r"$t/\tau$"); a.legend(fontsize=10, loc="lower right", framealpha=0.95); a.set_ylim(0, 2.05)
    axs[0].set_ylabel(r"$y/KM$")
    save(fig, "f08_second_order.png")


def fig_features():
    z, tau = 0.3, 1.0; t = np.linspace(0, 25, 5001); y = step(ct.tf(1, [1, 2 * z, 1]), t)
    wd = np.sqrt(1 - z ** 2) / tau; tp = np.pi / wd; P = 2 * np.pi / wd; OS = np.exp(-np.pi * z / np.sqrt(1 - z ** 2))
    tr = (np.pi - np.arccos(z)) / wd; ts = 4 * tau / z
    fig, axs = plt.subplots(1, 2, figsize=(12.4, 4.2), gridspec_kw={"width_ratios": [1.4, 1]})
    a = axs[0]; a.plot(t, y, color=NAVY, lw=2.4)
    a.axhline(1, color=GRAY, ls="--", lw=1); a.axhspan(0.98, 1.02, color=GREEN, alpha=0.12)
    a.annotate("", xy=(tp, 1 + OS), xytext=(tp, 1), arrowprops=dict(arrowstyle="<->", color=RED)); a.text(tp + 0.3, 1 + OS / 2, "$a$", color=RED, fontsize=14)
    a.annotate("", xy=(tp + P, 1 + OS ** 3), xytext=(tp + P, 1), arrowprops=dict(arrowstyle="<->", color=RED))
    a.text(tp + P + 0.3, 1.06, "$c$", color=RED, fontsize=14)
    a.annotate("", xy=(tp + P, 1.72), xytext=(tp, 1.72), arrowprops=dict(arrowstyle="<->", color=NAVY))
    a.text(tp + P / 2, 1.76, "period $P$", color=NAVY, ha="center")
    for x, lab in [(tr, "$t_r$"), (tp, "$t_p$"), (ts, "$t_s$ (2%)")]:
        a.axvline(x, color=GRAY, lw=0.8, ls=":"); a.text(x, -0.13, lab, ha="center", color="k")
    a.annotate("", xy=(0.6, 1), xytext=(0.6, 0), arrowprops=dict(arrowstyle="<->", color=NAVY)); a.text(0.15, 0.5, "$b$", color=NAVY, fontsize=14)
    a.set_ylim(-0.2, 1.9); a.set_xlabel(r"$t/\tau$"); a.set_title(rf"Underdamped step response, $\zeta={z}$")
    a = axs[1]; zz = np.linspace(0.001, 0.999, 400)
    os_ = np.exp(-np.pi * zz / np.sqrt(1 - zz ** 2))
    a.plot(zz, os_, color=RED, lw=2.4, label=r"overshoot $a/b$"); a.plot(zz, os_ ** 2, color=GREEN, lw=2.4, label=r"decay ratio $c/a$")
    a.plot(zz, np.sqrt(1 - zz ** 2), color=NAVY, lw=2.4, label=r"$2\pi\tau/P=\sqrt{1-\zeta^2}$")
    a.axhline(0.25, color=GRAY, lw=0.8, ls=":"); a.text(0.03, 0.27, "quarter decay: $\\zeta=0.215$", fontsize=10, color=GRAY)
    a.set_xlabel(r"$\zeta$"); a.legend(fontsize=10.5, loc="upper right"); a.set_title(r"Characteristics versus $\zeta$")
    save(fig, "f09_features.png")


# ---------------------------------------------------------------- 1.7 dead time
def fig_pade():
    t = np.linspace(0, 50, 5001); G = ct.tf(1, [10, 1])
    ye = delayed(step(G, t), t, 3)
    n1, d1 = ct.pade(3, 1); n2, d2 = ct.pade(3, 2)
    y1 = step(G * ct.tf(n1, d1), t); y2 = step(G * ct.tf(n2, d2), t)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.0))
    for a, lim in ((axs[0], (0, 50)), (axs[1], (0, 8))):
        a.plot(t, ye, color="k", lw=2.4, label=r"exact $e^{-3s}$")
        a.plot(t, y1, color=RED, lw=2, ls="--", label="1/1 Padé")
        a.plot(t, y2, color=NAVY, lw=2, ls="-.", label="2/2 Padé")
        a.set_xlim(*lim); a.set_xlabel("$t$"); a.legend(fontsize=10.5, loc="lower right" if lim[1] > 10 else "upper left")
    axs[1].set_ylim(-0.08, 0.45); axs[0].set_title(r"Ex 1.10: $e^{-3s}/(10s+1)$, unit step"); axs[1].set_title("zoom: Padé starts with an inverse response")
    save(fig, "f10_pade.png")


# ---------------------------------------------------------------- 1.8 higher order
def fig_tanks_series():
    t = np.linspace(0, 45, 4501); G = ct.tf(1, [3, 1]); Gn = G
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    for n, c in zip(range(1, 6), COL):
        ax.plot(t, step(Gn, t), color=c, lw=2.2, label=f"$n={n}$"); Gn = Gn * G
    ax.set_xlabel("$t$"); ax.set_ylabel(r"$h_n/(R_nM)$"); ax.legend(fontsize=10.5, loc="lower right")
    ax.set_title(r"$n$ identical tanks, $\tau=3$: more tanks, more sluggish, S-shaped")
    save(fig, "f11_tanks_series.png")


def approx_models():
    G = ct.tf(3, np.polymul(np.polymul([0.1, 1], [0.5, 1]), np.polymul([1, 1], [3, 1])))
    return G, [("FOPDT, slide rule: $3e^{-1.6s}/(3s+1)$", 3, [3, 1], 1.6, RED, "--"),
               ("SOPDT, slide rule: $3e^{-0.6s}/[(s+1)(3s+1)]$", 3, np.polymul([1, 1], [3, 1]), 0.6, GREEN, "--"),
               ("FOPDT, half rule: $3e^{-1.1s}/(3.5s+1)$", 3, [3.5, 1], 1.1, ORANGE, ":"),
               ("SOPDT, half rule: $3e^{-0.35s}/[(1.25s+1)(3s+1)]$", 3, np.polymul([1.25, 1], [3, 1]), 0.35, PURPLE, ":")]


def fig_lowfit():
    t = np.linspace(0, 15, 3001); G, ms = approx_models(); y = step(G, t)
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.plot(t, y, color="k", lw=3, label="full 4th order")
    for lab, K, den, th, c, ls in ms:
        ya = delayed(step(ct.tf(K, den), t), t, th); iae = np.trapezoid(abs(ya - y), t)
        ax.plot(t, ya, color=c, lw=2, ls=ls, label=f"{lab}   IAE {iae:.2f}")
    ax.set_xlabel("$t$"); ax.legend(fontsize=9.6, loc="lower right"); ax.set_title(r"Ex 1.11: $3/[(0.1s+1)(0.5s+1)(s+1)(3s+1)]$")
    save(fig, "f12_lowfit.png")


def fig_interacting():
    t = np.linspace(0, 20, 2001)
    Gni = ct.tf(1, np.polymul([1, 1], [1, 1])); Gi = ct.tf(1, [1, 3, 1])
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.plot(t, step(Gni, t), color=NAVY, lw=2.4, label=r"non-interacting $1/(s+1)^2$")
    ax.plot(t, step(Gi, t), color=RED, lw=2.4, label=r"interacting $1/(s^2+3s+1)$")
    ax.set_xlabel("$t$"); ax.set_ylabel(r"$h_2/(R_2 M)$"); ax.legend(fontsize=10.5, loc="lower right")
    ax.set_title(r"$A_1=A_2=R_1=R_2=1$: interaction slows the response")
    save(fig, "f13_interacting.png")


# ---------------------------------------------------------------- 1.9 zeros
def fig_leadlag():
    t = np.linspace(0, 18, 1801)
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    for tz, c, lab in [(4, RED, r"$\tau_z=4>\tau$: overshoot"), (2, GRAY, r"$\tau_z=\tau$: cancellation"),
                       (1, NAVY, r"$0<\tau_z=1<\tau$"), (0, GREEN, r"$\tau_z=0$: pure lag"), (-1, PURPLE, r"$\tau_z=-1<0$: inverse response")]:
        ax.plot(t, step(ct.tf([tz, 1], [2, 1]), t), color=c, lw=2.2, label=lab)
    ax.axhline(0, color="k", lw=0.6); ax.text(0.4, 1.85, r"$y(0^+)=\tau_z/\tau$", color=RED, fontsize=13)
    ax.set_xlabel("$t$"); ax.legend(fontsize=10.2, loc="lower right"); ax.set_title(r"Lead-lag $(\tau_zs+1)/(\tau s+1)$, $\tau=2$, unit step")
    save(fig, "f14_leadlag.png")


def fig_parallel():
    t = np.linspace(0, 18, 1801); K1, K2 = 3.0, -1.0
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.4), sharey=True)
    for a, (t1, t2, ttl) in zip(axs, [(2, 2, r"$\tau_1=\tau_2$"), (2, 0.5, r"$\tau_1\gg\tau_2$: inverse response"),
                                      (0.5, 2, r"$\tau_1\ll\tau_2$: overshoot")]):
        G1, G2 = ct.tf(K1, [t1, 1]), ct.tf(K2, [t2, 1])
        a.plot(t, step(G1, t), color=RED, lw=1.4, ls="--", label=r"$K_1/(\tau_1s+1)$")
        a.plot(t, step(G2, t), color=NAVY, lw=1.4, ls="--", label=r"$K_2/(\tau_2s+1)$")
        a.plot(t, step(G1 + G2, t), color="k", lw=2.6, label="sum")
        a.set_title(ttl); a.set_xlabel("$t$"); a.axhline(0, color="k", lw=0.6)
    axs[0].legend(fontsize=10, loc="center right"); axs[0].set_ylabel(r"$y$  ($K_1=3,\ K_2=-1$)")
    save(fig, "f15_parallel.png")


if __name__ == "__main__":
    for f in (fig_linearize, fig_inputs, fig_terms, fig_poles, fig_first_order, fig_ramp, fig_two_tanks,
              fig_second_order, fig_features, fig_pade, fig_tanks_series, fig_lowfit, fig_interacting,
              fig_leadlag, fig_parallel):
        f()
    print(sorted(p.name for p in OUT.glob("*.png")))
