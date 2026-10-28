"""Tiny time-domain simulator for loops with dead time (exact delay, no Padé).

Each block is advanced with a fixed step ``dt``; a first-order lag is discretized
exactly (zero-order hold) and a delay is a FIFO buffer of round(theta/dt) samples.

    G = FOPDT(K=0.8, tau=5, theta=2)      # 0.8 e^{-2s} / (5s+1)
    C = PI(Kc=2, tauI=5)
    for k in range(n): y = G(C(r - y))
"""
from collections import deque
import numpy as np

DT = 0.01


class Delay:
    def __init__(self, theta, dt=DT):
        n = int(round(theta / dt))
        self.buf = deque([0.0] * n) if n > 0 else None

    def __call__(self, u):
        if self.buf is None:
            return u
        self.buf.append(u)
        return self.buf.popleft()


class FOPDT:
    """K e^{-theta s} / (tau s + 1);  tau = 0 gives a pure gain (with delay)."""

    def __init__(self, K, tau, theta=0.0, dt=DT):
        self.K, self.y = K, 0.0
        self.a = np.exp(-dt / tau) if tau > 0 else 0.0
        self.delay = Delay(theta, dt)

    def __call__(self, u):
        u = self.delay(u)
        self.y = self.a * self.y + (1 - self.a) * self.K * u
        return self.y


class LeadLag:
    """K (tau_ld s + 1) e^{-theta s} / (tau_lg s + 1)."""

    def __init__(self, K, tau_ld, tau_lg, theta=0.0, dt=DT):
        self.K, self.r = K, tau_ld / tau_lg
        self.lag = FOPDT(1.0, tau_lg, 0.0, dt)
        self.delay = Delay(theta, dt)

    def __call__(self, u):
        u = self.delay(u)
        # (tau_ld s+1)/(tau_lg s+1) = r + (1-r)/(tau_lg s+1)
        return self.K * (self.r * u + (1 - self.r) * self.lag(u))


class PI:
    def __init__(self, Kc, tauI, dt=DT):
        self.Kc, self.tauI, self.dt, self.I = Kc, tauI, dt, 0.0

    def __call__(self, e):
        self.I += e * self.dt
        return self.Kc * (e + self.I / self.tauI)


def simulate_2x2(G, Kc, tauI, D12=None, D21=None, r1=1.0, r2=0.0, tf=80.0, dt=DT):
    """Two PI loops on a 2x2 process  G[i][j] = (K, tau, theta),  optional decouplers.

    D12 acts on controller-2 output and adds to M1; D21 acts on controller-1 output and adds to M2.
    Each decoupler is None, a number (static) or a (K, tau_ld, tau_lg, theta) tuple (lead-lag).
    Returns t, c1, c2, m1, m2.
    """
    g = [[FOPDT(*G[i][j], dt=dt) for j in range(2)] for i in range(2)]
    c = [PI(Kc[0], tauI[0], dt), PI(Kc[1], tauI[1], dt)]

    def mk(D):
        if D is None:
            return lambda u: 0.0
        if np.isscalar(D):
            return lambda u: D * u
        return LeadLag(*D, dt=dt)

    d12, d21 = mk(D12), mk(D21)
    n = int(round(tf / dt)) + 1
    out = np.zeros((n, 5))
    y1 = y2 = 0.0
    for k in range(n):
        u1, u2 = c[0](r1 - y1), c[1](r2 - y2)
        m1, m2 = u1 + d12(u2), u2 + d21(u1)
        y1 = g[0][0](m1) + g[0][1](m2)
        y2 = g[1][0](m1) + g[1][1](m2)
        out[k] = k * dt, y1, y2, m1, m2
    return out.T
