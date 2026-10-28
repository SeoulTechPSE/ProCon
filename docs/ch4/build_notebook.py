"""Build the companion Colab notebook ch4_stability.ipynb."""
import nbformat as nbf
from pathlib import Path

routh_src = Path(__file__).with_name("routh.py").read_text().split('if __name__')[0]

cells = []
md = lambda t: cells.append(nbf.v4.new_markdown_cell(t))
code = lambda t: cells.append(nbf.v4.new_code_cell(t))

md("""# Ch.4 Stability of Closed-Loop Systems — companion notebook
Process Dynamics and Control · SeoulTech

Python versions of every calculation and figure in the slides (`python-control`, `scipy`, `sympy`).""")
code("""%pip install -q control   # Colab: python-control is not preinstalled""")
code("""import numpy as np, sympy as sp, control as ct, matplotlib.pyplot as plt
from scipy.optimize import brentq
plt.rcParams.update({'figure.dpi': 110, 'axes.grid': True})
s, Kc, tI, w = sp.symbols('s K_c tau_I omega', real=True)

def rlocus(sys, xlim=None, ylim=None, ax=None, **kw):
    # root_locus_plot + axis limits without the equal-aspect warning
    if ax is None:                   # let python-control create the axes (needed for grid=True)
        ct.root_locus_plot(sys, **kw); ax = plt.gca()
    else:
        ct.root_locus_plot(sys, ax=ax, **kw)
    ax.set_aspect('auto')            # python-control sets aspect='equal'; release it before fixing limits
    if xlim: ax.set_xlim(xlim)
    if ylim: ax.set_ylim(ylim)
    return ax""")

md("## Routh array helper (handles the ε case and a row of zeros)")
code(routh_src)

md("## 4.2 Routh–Hurwitz\n### Example 4.2 — P control of 1/[(s+1)(s+2)(s+3)]")
code("""R = routh_array((s+3)*(s+2)*(s+1) + Kc, s)
sp.solve([r[0] > 0 for r in R], Kc)""")
md("### Special case 2 — Ex 4.2 at the ultimate gain $K_c=60$")
code("""R = routh_array((s+3)*(s+2)*(s+1) + 60, s)""")
md("### Special case 1 — zero in the first column")
code("""R = routh_array(s**4 + s**3 + 2*s**2 + 2*s + 3, s)
print('first column as eps -> 0+ :', [sp.limit(c, eps, 0, '+') for c in first_column(R)])
print('roots:', np.roots([1, 1, 2, 2, 3]))""")
md("### Example 4.3 — PI control of 1/(s+1)²")
code("""tIp, Kcp = sp.symbols('tau_I K_c', positive=True)
R = routh_array(tIp*s*(s**2 + 2*s + 1) + Kcp*(tIp*s + 1), s)
boundary = sp.solve(sp.Eq(R[2][0], 0), tIp)[0]
boundary   # tau_I > Kc / (2 (1 + Kc))""")

md("## 4.3 Direct substitution\n### Example 4.2A")
code("""eq = sp.expand(((s+1)*(s+2)*(s+3) + Kc).subs(s, sp.I*w))
sp.solve([sp.re(eq), sp.im(eq)], [w, Kc], dict=True)""")
md("### Example 4.4 — dead time: exact vs. Padé")
code("""wu  = brentq(lambda w: 2*w + np.arctan(5*w) - np.pi, 0.1, 2.0)
Kcu = np.sqrt(1 + 25*wu**2)/0.8
print(f'exact : wu = {wu:.4f}, Kcu = {Kcu:.4f}')

G = ct.tf(0.8, [5, 1])
for order in (1, 3, 10):
    gm, pm, wcg, wcp = ct.margin(G*ct.tf(*ct.pade(2, order)))
    print(f'Pade {order:2d}: wu = {wcg:.4f}, Kcu = {gm:.4f}')""")
code("""t = np.linspace(0, 60, 3000)
fig, axs = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
for ax, order in zip(axs, (10, 1)):
    D = ct.tf(*ct.pade(2, order))
    for K in (5.0, 5.73, 6.5):
        _, y = ct.step_response(ct.feedback(K*G*D, 1), t)
        ax.plot(t, y, label=f'Kc={K}')
    ax.set_ylim(-1.5, 2.5); ax.set_title(f'Padé order {order}'); ax.legend()""")
md("### Ultimate gain → Ziegler–Nichols settings")
code("""for name, Ku, wu_ in [('Ex 4.2', 60, np.sqrt(11)), ('Ex 4.4', Kcu, wu)]:
    Pu = 2*np.pi/wu_
    print(f'{name}: Kcu={Ku:.2f} Pu={Pu:.3f} | P: {0.5*Ku:.2f} | PI: {0.45*Ku:.2f}, {Pu/1.2:.3f} | '
          f'PID: {0.6*Ku:.2f}, {Pu/2:.3f}, {Pu/8:.3f}')""")

md("## 4.4 Root locus\n### Angle and magnitude conditions at $s=j\\sqrt{11}$ (Ex 4.2)")
code("""sp_ = 1j*np.sqrt(11); poles = np.array([-1, -2, -3])
print('sum of angles [deg]:', np.degrees(np.sum(np.angle(sp_ - poles))))
print('Kc = prod|s-p| =', np.prod(np.abs(sp_ - poles)))""")
md("### Example 4.2B")
code("""G42 = ct.tf(1, np.poly([-1, -2, -3]))
rlocus(G42, xlim=(-7, 1.5), ylim=(-5, 5))
print('break-away candidates:', np.roots([3, 12, 11]))""")
md("### Example 4.6 — representative shapes")
code("""cases = [ct.tf(1, np.poly([-1, -2])), ct.tf(1, [1, 4, 5]),
         ct.tf([1, 2.5], np.poly([-1, -2])), ct.tf([1, 3], [1, 4, 5])]
fig, axs = plt.subplots(1, 4, figsize=(16, 3.8))
for ax, Gi in zip(axs, cases):
    rlocus(Gi, xlim=(-6, 1), ylim=(-2.5, 2.5), ax=ax)
P, Q = (s+2)*(s+1), s + sp.Rational(5, 2)
print('(c) break points:', sp.solve(sp.expand(Q*sp.diff(P, s) - P*sp.diff(Q, s)), s))
pz, p1, p2 = -3, -2+1j, -2-1j
print('(d) departure from -2-j [x pi]:', (np.angle(p2-pz) - np.angle(p2-p1) - np.pi)/np.pi)""")
md("### Effect of an added zero / pole")
code("""fig, axs = plt.subplots(1, 3, figsize=(15, 4))
den = np.poly([-1, -2, -3])
for ax, num in zip(axs, ([1], [1, 1.5], np.poly([-1.5, -2.5]))):
    rlocus(ct.tf(num, den), xlim=(-7, 1.5), ylim=(-6, 6), ax=ax)""")
code("""# Example 4.3B: PI adds a pole at 0 and a zero at -1/tau_I
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
for ax, tau in zip(axs, (0.2, 0.6)):
    ct.root_locus_plot(ct.tf([tau, 1], tau*np.poly([0, -1, -1])), ax=ax); ax.set_title(f'tau_I = {tau}')
print('tau_I = 0.2 -> Kc,max =', 2*0.2/(1 - 2*0.2))""")
md("### RHP zero (inverse response)")
code("""Grhp = ct.tf([-1, 1], [2, 3, 1])
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
ct.root_locus_plot(Grhp, ax=axs[0])
t, y = ct.step_response(Grhp, np.linspace(0, 10, 400)); axs[1].plot(t, y); axs[1].set_title('inverse response')
for K in (2.9, 3.1):
    print(K, ct.feedback(K*Grhp, 1).poles())""")

md("## 4.5 Root-locus design\n### Example 4.7 — $\\zeta = 0.7$ with P control")
code("""G47 = ct.tf(1, np.polymul([2, 1], [4, 1]))
zeta = 0.7
Kc47 = 9/(8*zeta**2) - 1           # from zeta = 3/sqrt(8(1+Kc))
T = ct.feedback(Kc47*G47, 1)
print('Kc =', Kc47, ' poles:', T.poles()); print(ct.step_info(T)); print('offset =', 1/(1 + Kc47))
rlocus(G47, xlim=(-0.8, 0.1), ylim=(-0.8, 0.8), grid=True);""")
md("### Example 4.8 — PI design")
code("""for tau in (3, sp.Rational(2, 3)):
    a2, a1, a0 = sp.Poly(sp.expand(tau*s*(2*s + 1) + sp.Rational(1, 2)*Kc*(tau*s + 1)), s).all_coeffs()
    sol = sp.solve(sp.Eq(a1**2, 4*sp.Rational(49, 100)*a2*a0), Kc)
    print('tau_I =', tau, '-> Kc for zeta=0.7:', [sp.N(x, 4) for x in sol if x.is_real])
for K in (0.5552, 7.2048):
    T = ct.feedback(ct.tf([K*0.5*2/3, K*0.5], np.polymul([2/3, 0], [2, 1])), 1)
    info = ct.step_info(T)
    print(f'Kc={K}: poles {np.round(T.poles(), 3)}, OS={info["Overshoot"]:.1f} %, ts={info["SettlingTime"]:.2f}')""")

md("## Problem #1 — (homework) start here")
code("""Gp1 = ct.tf([2, 2], np.polymul([1, 2, 0], [1, 0, 1]))
# (a) characteristic polynomial with Gc = Kc -> routh_array(...)
# (b) write Gc for PI and PD, then compare root-locus plots
""")

nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, Path(__file__).with_name("ch4_stability.ipynb"))
print("written", len(cells), "cells")
