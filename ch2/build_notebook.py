"""Build the companion Colab notebook ch2_analysis.ipynb."""
import nbformat as nbf
from pathlib import Path

cells = []
md = lambda t: cells.append(nbf.v4.new_markdown_cell(t))
code = lambda t: cells.append(nbf.v4.new_code_cell(t))

md("""# Ch.2 Analysis of Single-Loop Control Systems — companion notebook
Process Dynamics and Control · SeoulTech

Python versions of every derivation (`sympy`), calculation and figure in the slides (`python-control`, `numpy`).""")
code(r"""%pip install -q control   # Colab: python-control is not preinstalled""")
code(r"""import numpy as np, sympy as sp, control as ct, matplotlib.pyplot as plt
from IPython.display import display, Math
plt.rcParams.update({'figure.dpi': 110, 'axes.grid': True, 'mathtext.fontset': 'cm'})
step = lambda sysm, t: np.asarray(ct.step_response(sysm, t).outputs, float).ravel()
s = sp.Symbol('s')
show = lambda lhs, e: display(Math(lhs + ' = ' + sp.latex(e)))

def pid(Kc, tI=None, tD=0.0, alpha=0.1):
    '''Ideal PID with a filtered derivative  Kc[1 + 1/(tI s) + tD s/(alpha tD s + 1)].'''
    C = ct.tf(Kc, 1)
    if tI: C = C + ct.tf(Kc, [tI, 0])
    if tD: C = C + ct.tf([Kc*tD, 0], [alpha*tD, 1])
    return C""")

md("## 2.1 Block-diagram algebra\nThe standard loop: $C = G_{sp}R + G_{load}L$.")
code(r"""Km, Gc, Ga, Gp, GL, Gm, R, L, C = sp.symbols('K_m G_c G_a G_p G_L G_m R L C')
E = Km*R - Gm*C                                   # comparator, in mA
sol = sp.solve(sp.Eq(C, Gp*Ga*Gc*E + GL*L), C)[0]
show('G_{sp}', sp.simplify(sol.diff(R))); show('G_{load}', sp.simplify(sol.diff(L)))""")

md("### Transmitter: 20–120 °C → 4–20 mA")
code(r"""m = (20 - 4)/(120 - 20); I0 = 4 - 20*m
print(f'm = {m:.2f} mA/degC, I0 = {I0:.2f} mA')
print(f'66 degC -> {m*66 + I0:.2f} mA;  6.5 mA -> {(6.5 - I0)/m:.1f} degC')""")

md("### Valve characteristics")
code(r"""l = np.linspace(0, 1, 201)
plt.plot(l, np.sqrt(l), label='quick opening'); plt.plot(l, l, label='linear')
plt.plot(l, 40.0**(l - 1), label='equal percentage (R = 40)')
plt.xlabel(r'lift $\ell$'); plt.ylabel(r'$f(\ell)$'); plt.legend();""")

md("### The heater loop under P control")
code(r"""Gp_h, Gv_h, Km_h = ct.tf(0.85, [20, 1]), ct.tf(0.6, [0.2, 1]), 0.16
t = np.linspace(0, 60, 3001)
for Kc in (5, 10, 20, 50):
    KOL = Kc*0.6*0.85*Km_h
    plt.plot(t, step(ct.feedback(Km_h*Kc*Gv_h*Gp_h, 1), t), label=f'Kc={Kc}: offset {1/(1 + KOL):.0%}')
plt.xlabel('time (min)'); plt.legend();""")

md("## 2.2 PID modes on $G_p = G_L = 1/(s+1)^3$ (load step)")
code(r"""G3 = ct.tf(1, [1, 3, 3, 1]); t = np.linspace(0, 25, 3001)
plt.plot(t, step(G3, t), label='no control')
for lab, Cc in [('P', pid(2)), ('PI', pid(2, 2.5)), ('PID', pid(3, 2, 0.6))]:
    plt.plot(t, step(ct.feedback(G3, Cc), t), label=lab)
plt.xlabel('time'); plt.legend();""")

md("### Reset windup and anti-windup (clamping)")
code(r"""A, B, Cm, _ = (np.asarray(M) for M in ct.ssdata(ct.tf2ss(G3))); B = B.ravel(); Cm = Cm.ravel()
dt, T, Kc, tI, umax = 0.002, 40, 2.5, 2.0, 1.25
for aw in (False, True):
    x = np.zeros(3); I = 0.0; ys = []
    for k in range(int(T/dt)):
        y = Cm @ x; e = 1 - y
        v = Kc*(e + I/tI); u = np.clip(v, -umax, umax)
        if not aw or v == u or np.sign(e) != np.sign(v):    # clamp: freeze I while saturated
            I += e*dt
        x = x + dt*(A @ x + B*u); ys.append(y)
    plt.plot(np.arange(len(ys))*dt, ys, label='anti-windup' if aw else 'no anti-windup')
plt.axhline(1, ls=':'); plt.xlabel('time'); plt.legend();""")

md("## 2.3 Closed-loop responses — Examples 2.1–2.5 with sympy")
code(r"""Kc, Kp, tp, tI, tD, t1, t2 = sp.symbols('K_c K_p tau_p tau_I tau_D tau_1 tau_2', positive=True)
CL = lambda Gc_, Gp_: sp.factor(sp.cancel(Gc_*Gp_/(1 + Gc_*Gp_)))
G1 = Kp/(tp*s + 1)
for ex, Gc_, Gp_ in [('2.1', Kc, G1),
                     ('2.2', Kc, Kp/((t1*s + 1)*(t2*s + 1))),
                     ('2.3', Kc*(1 + 1/(tI*s)), G1),
                     ('2.4', Kc*(1 + tD*s), G1),
                     ('2.5', Kc, Kp/s)]:
    T_ = CL(Gc_, Gp_)
    display(Math(rf'\text{{Ex {ex}:}}\ G_c = {sp.latex(Gc_)},\ G_p = {sp.latex(Gp_)}:\quad '
                 rf'\frac{{C}}{{R}} = {sp.latex(T_)}, \qquad e(\infty) = {sp.latex(sp.simplify(1 - T_.subs(s, 0)))}'))""")

md("### Example 2.2 — $K_c$ for $\\zeta = 0.7$")
code(r"""den = sp.Poly(sp.expand((2*s + 1)*(4*s + 1) + Kc), s).all_coeffs()     # a2 s^2 + a1 s + a0
zeta = den[1]/(2*sp.sqrt(den[0]*den[2]))
Kc22 = sp.solve(sp.Eq(zeta, sp.Rational(7, 10)), Kc)[0]
print('Kc =', float(Kc22), ' offset =', float(1/(1 + Kc22)))
t = np.linspace(0, 30, 3001)
for k in (0.3, float(Kc22), 5):
    plt.plot(t, step(ct.feedback(k*ct.tf(1, [8, 6, 1]), 1), t), label=f'Kc = {k:.3g}')
plt.legend(); plt.xlabel('time');""")

md("### Example 2.3 — $\\tau$ and $\\zeta$ of the PI loop")
code(r"""num, den = sp.fraction(sp.cancel(CL(Kc*(1 + 1/(tI*s)), G1)))
a = sp.Poly(den, s).all_coeffs()
tau = sp.sqrt(a[0]/a[2]); zeta = sp.simplify(a[1]/a[2]/(2*tau))
show(r'\tau', sp.simplify(tau)); show(r'\zeta', zeta)""")

md("### Example 2.5 — integrating process: servo versus regulator")
code(r"""Gi = ct.tf(1, [1, 0]); Kc5 = 0.8; t = np.linspace(0, 12, 2001)
plt.plot(t, step(ct.feedback(Kc5*Gi, 1), t), label='set-point step')
plt.plot(t, step(ct.feedback(Gi, Kc5), t), label=f'load step, P: C -> 1/Kc = {1/Kc5:.2f}')
plt.plot(t, step(ct.feedback(Gi, pid(Kc5, 2)), t), label='load step, PI')
plt.legend(); plt.xlabel('time');""")

md("### Example 2.6 — simulation")
code(r"""Gp6 = ct.tf(0.8, [5, 1]); t = np.linspace(0, 6, 601)
for lab, Gc_ in [('P', 10), ('PI', ct.tf([10, 10], [1, 0]))]:
    Gcl = ct.feedback(Gp6*Gc_, 1); y = step(Gcl, t)
    print(f'{lab}: final {ct.dcgain(Gcl):.3f}, peak {y.max():.3f}')
    plt.plot(t, y, label=lab)
print(ct.damp(ct.feedback(Gp6*ct.tf([10, 10], [1, 0]), 1)))
plt.legend(); plt.xlabel('time');""")

md("## Problems #2 and #3 — (homework) start here")
code(r"""# Problem #2: transmitter span 50 degF, zero 55 degF  ->  Km = 16/50 mA/degF
Km2, Kc2, Kv2, KIP2 = 16/50, 5, 1.2, 0.75
# P control: dT/dTsp at steady state = KOL/(1 + KOL), KOL = Km*Kc*KIP*Kv*K2  -> solve for K2

# Problem #3: transmitter 3-9 lb/ft^3 -> 4-20 mA; valve table p_t = 6, 9, 12 psi -> q2 = 20, 15, 10 gal/min
pt = np.array([6, 9, 12]); q2 = np.array([20, 15, 10])
""")

nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, Path(__file__).with_name("ch2_analysis.ipynb"))
print("written", len(cells), "cells")
