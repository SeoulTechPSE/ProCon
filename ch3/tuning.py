"""PID tuning relations used in Ch.3 (FOPDT model  K e^{-theta s}/(tau s + 1)).

Every function returns (Kc, tauI, tauD); tauI = None for P, tauD = 0 for P/PI.
    from tuning import RULES
    RULES['ITAE set point']('PID', K=1, tau=2.57, theta=1.14)
"""
import numpy as np
import control as ct


def zn_prc(ctrl, K, tau, theta):
    r = tau / theta
    return {"P": (r / K, None, 0.0),
            "PI": (0.9 * r / K, 3.3 * theta, 0.0),
            "PID": (1.2 * r / K, 2.0 * theta, 0.5 * theta)}[ctrl]


def cohen_coon(ctrl, K, tau, theta):
    r, q = tau / theta, theta / tau
    return {"P": ((r + 1 / 3) / K, None, 0.0),
            "PI": ((0.9 * r + 1 / 12) / K, theta * (30 + 3 * q) / (9 + 20 * q), 0.0),
            "PID": ((4 / 3 * r + 1 / 4) / K, theta * (32 + 6 * q) / (13 + 8 * q), theta * 4 / (11 + 2 * q))}[ctrl]


_ITAE = {("load", "PI"): (0.859, 0.977, 0.674, 0.680, None, None),
         ("load", "PID"): (1.357, 0.947, 0.842, 0.738, 0.381, 0.995),
         ("sp", "PI"): (0.586, 0.916, 1.03, 0.165, None, None),
         ("sp", "PID"): (0.965, 0.855, 0.796, 0.147, 0.308, 0.929)}


def itae(ctrl, K, tau, theta, mode="sp"):
    a1, b1, a2, b2, a3, b3 = _ITAE[(mode, ctrl)]
    q = theta / tau
    Kc = a1 / K * (1 / q) ** b1
    tI = tau / a2 * q ** b2 if mode == "load" else tau / (a2 - b2 * q)
    tD = a3 * tau * q ** b3 if a3 else 0.0
    return Kc, tI, tD


def imc(ctrl, K, tau, theta, tauc=None):
    """IMC with 1st-order Padé (Ex 3.5); PI version = direct synthesis of Ex 3.3."""
    tauc = theta if tauc is None else tauc
    if ctrl == "PI":
        return tau / (K * (tauc + theta)), tau, 0.0
    return (2 * tau / theta + 1) / (K * (2 * tauc / theta + 1)), tau + theta / 2, tau / (2 * tau / theta + 1)


RULES = {"Ziegler–Nichols (PRC)": zn_prc,
         "Cohen–Coon": cohen_coon,
         "ITAE set point": lambda c, K, t, th: itae(c, K, t, th, "sp"),
         "ITAE load": lambda c, K, t, th: itae(c, K, t, th, "load"),
         "IMC (τc = θ)": imc}


def pid_tf(Kc, tauI=None, tauD=0.0, alpha=0.1):
    """Ideal PID with filtered derivative  Kc[1 + 1/(tauI s) + tauD s/(alpha tauD s + 1)]."""
    if tauI is None:
        return ct.tf(Kc, 1)
    if not tauD:
        return ct.tf([Kc * tauI, Kc], [tauI, 0])
    return ct.tf(Kc * np.array([(alpha + 1) * tauD * tauI, tauI + alpha * tauD, 1.0]),
                 [alpha * tauD * tauI, tauI, 0])


def fit_two_point(t, y, du=1.0):
    """Two-point (Smith) FOPDT fit from t28 and t63 of a step response of size du."""
    yinf = y[-1]; K = yinf / du; yn = y / yinf
    t28, t63 = t[np.argmax(yn >= 0.283)], t[np.argmax(yn >= 0.632)]
    tau = 1.5 * (t63 - t28)
    return K, tau, t63 - tau


def fit_tangent(t, y, du=1.0):
    """Tangent at the inflection point (Ziegler–Nichols' original construction)."""
    yinf = y[-1]; K = yinf / du
    dy = np.gradient(y, t); i = int(np.argmax(dy))
    theta = t[i] - y[i] / dy[i]
    return K, yinf / dy[i], theta
