"""Running case study: the stirred-tank heater, followed through Chapters 1-6.

    python case/heater.py        # prints every number used on case.qmd and writes case/figures/*.png

Model (Ex 1.2 / Ch 2):  T = Gp*T_H + GL*T_i,  tau_p = 20 min, K_p = 0.85, K_d = 0.15  (kappa = 5.67)
Loop (Ch 2):            Gc (mA/mA) -> Gv = 0.6/(0.2s+1) (degC/mA) -> Gp -> T -> Gm = 0.16/(s+1) (mA/degC)
"""
import numpy as np
import sympy as sp
import control as ct
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).parent / "figures"; OUT.mkdir(exist_ok=True)
NAVY, RED, GREEN, ORANGE, GRAY = "#333399", "#C00000", "#2E7D32", "#E07B00", "#888888"
plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 150, "savefig.bbox": "tight", "mathtext.fontset": "cm", "axes.grid": True,
                     "grid.color": "#e3e3e3", "grid.linewidth": 0.6})
s = ct.tf("s")
kappa = 0.85 / 0.15
Gp, GL = 0.85 / (20 * s + 1), 0.15 / (20 * s + 1)
Gv, Gm, Km = 0.6 / (0.2 * s + 1), 0.16 / (s + 1), 0.16
G = Gv * Gp * Gm                                  # everything the controller "sees"
t = np.linspace(0, 60, 6001)
y_ = lambda sys_, tt=t: np.asarray(ct.step_response(sys_, tt).outputs, float).ravel()
N = {}                                            # numbers quoted on the page


def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name); plt.close(fig)


def ch1():
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.plot(t, 10 * y_(Gp), color=RED, lw=2.3, label=r"$T_H$ step $+10$ °C: $\Delta T\to8.5$ °C")
    ax.plot(t, 10 * y_(GL), color=NAVY, lw=2.3, label=r"$T_i$ step $+10$ °C: $\Delta T\to1.5$ °C")
    ax.axvline(20, color=GRAY, ls=":"); ax.text(20.8, 3.0, r"$\tau_p=20$ min", color=GRAY)
    ax.set_xlabel("time (min)"); ax.set_ylabel(r"$T'$ (°C)"); ax.legend(fontsize=10.5, loc="center right")
    ax.set_title("Open loop: one pole, two inputs")
    save(fig, "c1_open_loop.png")


def ch2():
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    for Kc, tI, c, lab in ((20, None, ORANGE, "P, $K_c=20$"), (50, None, RED, "P, $K_c=50$"), (50, 5.6, NAVY, r"PI, $K_c=50,\ \tau_I=5.6$")):
        C = Kc * (1 + 1 / (tI * s)) if tI else ct.tf(Kc, 1)
        T = ct.feedback(Km * C * Gv * Gp, Gm / Km)
        yy = y_(T); ax.plot(t, yy, color=c, lw=2.2, label=f"{lab}: final {yy[-1]:.2f}")
        N[f"ch2_{lab}"] = yy[-1]
    ax.axhline(1, color=GRAY, ls=":"); ax.set_xlabel("time (min)"); ax.set_ylabel(r"$T'/T'_{sp}$")
    ax.set_ylim(0, 1.8); ax.legend(fontsize=10.5, loc="upper right"); ax.set_title("Unit set-point step: P leaves an offset, PI does not")
    save(fig, "c2_offset.png")


def ch3():
    K, tau, theta = 0.6 * 0.85 * 0.16, 20 + 1 / 2, 1 / 2 + 0.2            # half rule
    Kc, tI = tau / (K * 2 * theta), min(tau, 8 * theta)
    N.update(K=K, tau=tau, theta=theta, Kc=Kc, tI=tI)
    fo = np.where(t < theta, 0, K * (1 - np.exp(-(t - theta) / tau)))
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8))
    axs[0].plot(t, y_(G), color="k", lw=2.4, label="3rd-order loop $G_vG_pG_m$")
    axs[0].plot(t, fo, color=RED, lw=2, ls="--", label=rf"FOPDT: ${K:.4f}e^{{-{theta}s}}/({tau}s+1)$")
    axs[0].set_xlim(0, 20); axs[0].set_xlabel("time (min)"); axs[0].legend(fontsize=10); axs[0].set_title("half-rule model")
    C = Kc * (1 + 1 / (tI * s)); L = C * G
    yl = y_(-10 * GL / (1 + L)); N["load_min_simc"] = yl.min(); N["load_iae_simc"] = np.trapezoid(abs(yl), t)
    axs[1].plot(t, yl + 0, color=NAVY, lw=2.3, label=rf"SIMC PI $K_c={Kc:.0f},\ \tau_I={tI:.1f}$")
    axs[1].plot(t, -10 * y_(GL), color=GRAY, lw=1.8, ls=":", label="no control")
    axs[1].set_ylim(-1.7, 0.4); axs[1].axhline(0, color="k", lw=0.6)
    axs[1].set_xlabel("time (min)"); axs[1].set_ylabel(r"$T'$ (°C)"); axs[1].legend(fontsize=10, loc="lower right")
    axs[1].set_title(r"inlet temperature drops 10 °C")
    save(fig, "c3_simc.png")
    return C


def ch4():
    s_, Kc = sp.symbols("s K_c", positive=True)
    p = sp.Poly(sp.expand((sp.Rational(1, 5) * s_ + 1) * (20 * s_ + 1) * (s_ + 1)) + sp.Rational(816, 10000) * Kc, s_).all_coeffs()
    a3, a2, a1, a0 = p
    Kcu = sp.solve(sp.Eq(a2 * a1 - a3 * a0, 0), Kc)[0]; wu = sp.sqrt(a1 / a3)
    N.update(char=p, Kcu=float(Kcu), Pu=float(2 * sp.pi / wu.subs(Kc, Kcu)))
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    num, den = [0.0816], np.polymul(np.polymul([0.2, 1], [20, 1]), [1, 1])
    for k in np.r_[0, np.logspace(-2, 3.6, 900)]:
        r = np.roots(np.polyadd(den, k * np.array(num))); ax.plot(r.real, r.imag, ".", color=NAVY, ms=1.5)
    for pp in np.roots(den): ax.plot(pp.real, pp.imag, "x", color=RED, ms=10, mew=2)
    wuf = float(wu.subs(Kc, Kcu)); ax.plot([0, 0], [wuf, -wuf], "o", color=RED)
    ax.text(0.15, wuf, rf"$K_{{cu}}={float(Kcu):.0f}$, $\omega_u={wuf:.2f}$", color=RED)
    ax.axvline(0, color="k", lw=0.8); ax.set_xlim(-6, 2.2); ax.set_ylim(-4, 4)
    ax.set_xlabel("Re $s$"); ax.set_ylabel("Im $s$"); ax.set_title("Root locus, P control")
    save(fig, "c4_rlocus.png")


def ch5(C):
    L = C * G; gm, pm, wc, wg = ct.margin(L)
    w = np.logspace(-3, 2, 4000); Lj = L(1j * w); S = 1 / (1 + Lj)
    N.update(GM=gm, PM=pm, Ms=abs(S).max())
    fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.0), sharex=True)
    axs[0].loglog(w, abs(Lj), color=NAVY, lw=2); axs[0].axhline(1, color="k", lw=0.7)
    ph = np.degrees(np.unwrap(np.angle(Lj)))
    axs[1].semilogx(w, ph, color=NAVY, lw=2); axs[1].axhline(-180, color=RED, ls="--", lw=1)
    axs[0].plot(wc, 1 / gm, "o", color=RED); axs[0].text(wc * 1.2, 1 / gm, f"GM = {gm:.1f}", color=RED)
    axs[1].plot(wg, -180 + pm, "o", color=GREEN); axs[1].text(wg * 1.3, -180 + pm, f"PM = {pm:.0f}°", color=GREEN)
    axs[0].set_ylabel(r"$|L|$"); axs[1].set_ylabel(r"$\angle L$ (deg)"); axs[1].set_xlabel(r"$\omega$ (rad/min)")
    axs[0].set_title(rf"SIMC loop: GM {gm:.1f}, PM {pm:.0f}°, $M_s={abs(S).max():.2f}$"); axs[1].set_ylim(-280, 0)
    save(fig, "c5_bode.png")


def ch6(C):
    L = C * G
    yfb = y_(-10 * GL / (1 + L))
    Gff = -0.15 / (0.85 * 0.6)                                         # static: -0.294 mA per degC of T_i
    yff = y_(-10 * (GL + Gff * Gv * Gp) / (1 + L))
    N.update(Gff=Gff, fb_min=yfb.min(), ff_min=yff.min())
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.plot(t, yfb, color=RED, lw=2.2, label=f"feedback only: max dev {abs(yfb.min()):.3f} °C")
    ax.plot(t, yff, color=NAVY, lw=2.2, label=f"+ static feedforward: max dev {abs(yff.min()):.3f} °C")
    ax.axhline(0, color="k", lw=0.6); ax.set_xlabel("time (min)"); ax.set_ylabel(r"$T'$ (°C)")
    ax.legend(fontsize=10.5, loc="lower right"); ax.set_title(r"inlet temperature drops 10 °C")
    save(fig, "c6_feedforward.png")


if __name__ == "__main__":
    ch1(); ch2(); C = ch3(); ch4(); ch5(C); ch6(C)
    for k, v in N.items():
        print(f"{k:28s} {v}")
