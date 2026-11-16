"""Minimal dynamic-matrix (DMC-type) MPC for a FOPDT process, with input bounds.

    from mpc import fopdt_mpc
    t, y, u = fopdt_mpc(K=0.8, tau=5, theta=2, r=lambda t: 1.0, umin=0, umax=1.6)

At every sample: predict P steps ahead with the model, choose the next M inputs
(bounded) that minimize  sum (r - y)^2 + lam * sum (du)^2, apply the first, repeat.
"""
import numpy as np
from scipy.optimize import lsq_linear


def fopdt_mpc(K, tau, theta, r, umin=-np.inf, umax=np.inf, dt=0.5, T=30.0, P=30, M=6, lam=0.05,
              Kp=None, taup=None, thetap=None, load=lambda t: 0.0):
    """Plant parameters default to the model (perfect model); pass Kp, taup, thetap for mismatch."""
    Kp, taup, thetap = Kp or K, taup or tau, thetap if thetap is not None else theta
    a, nd = np.exp(-dt / tau), int(round(theta / dt))                 # model
    ap, ndp = np.exp(-dt / taup), int(round(thetap / dt))             # plant
    S = np.array([0.0 if j <= nd else K * (1 - a ** (j - nd)) for j in range(P + 1)])
    A = np.array([[S[j + 1 - i] if j + 1 - i >= 1 else 0.0 for i in range(M)] for j in range(P)])
    D = np.eye(M) - np.eye(M, k=-1); e1 = np.eye(M)[0]
    xm, bm, xp, bp, u_prev = 0.0, [0.0] * nd, 0.0, [0.0] * ndp, 0.0
    n = int(round(T / dt)); ts, ys, us = np.arange(n) * dt, np.zeros(n), np.zeros(n)
    for k in range(n):
        y = xp; bias = y - xm                                          # DMC output correction
        xf, bf, free = xm, list(bm), []
        for j in range(P):                                             # free response, u held
            ud = bf[0] if nd else u_prev
            xf = a * xf + K * (1 - a) * ud; bf = (bf[1:] + [u_prev]) if nd else bf
            free.append(xf + bias)
        rr = np.array([r(ts[k] + (j + 1) * dt) for j in range(P)])
        Au = np.vstack([A @ D, np.sqrt(lam) * D])
        bu = np.r_[rr - np.array(free) + A @ (e1 * u_prev), np.sqrt(lam) * e1 * u_prev]
        u = lsq_linear(Au, bu, bounds=(umin, umax)).x[0]
        for buf, ndd in ((bm, nd), (bp, ndp)):
            buf.append(u)
        um = bm.pop(0) if nd else u; up = bp.pop(0) if ndp else u
        xm = a * xm + K * (1 - a) * um
        xp = ap * xp + Kp * (1 - ap) * (up + load(ts[k]))
        ys[k], us[k], u_prev = y, u, u
    return ts, ys, us
