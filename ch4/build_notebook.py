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
code(r"""%pip install -q control   # Colab: python-control is not preinstalled""")
code(r"""import numpy as np, sympy as sp, control as ct, matplotlib.pyplot as plt
from scipy.optimize import brentq
from IPython.display import display, Math
plt.rcParams.update({'figure.dpi': 110, 'axes.grid': True, 'mathtext.fontset': 'cm'})
sp.init_printing()                   # sympy results render as LaTeX
s, Kc, tI, w = sp.symbols('s K_c tau_I omega', real=True)

def rlocus(sys, xlim=None, ylim=None, ax=None, title=None, zeta=None):
    # root locus on our own axes: no auto super-title, no cluttered s-grid, no equal-aspect warning
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4.5))
    ct.root_locus_plot(sys, ax=ax)
    ax.set_aspect('auto')            # python-control sets aspect='equal'; release it before fixing limits
    if zeta is not None:             # constant-damping rays  s = r(-zeta ± j sqrt(1-zeta^2))
        th = np.arccos(zeta)
        for sg in (1, -1):
            ax.plot([0, -50*np.cos(th)], [0, sg*50*np.sin(th)], 'g--', lw=1.2)
        ax.text(0.02, 0.95, rf'$\zeta={zeta}$', color='g', transform=ax.transAxes, va='top')
    if xlim: ax.set_xlim(xlim)
    if ylim: ax.set_ylim(ylim)
    ax.set_xlabel(r'$\mathrm{Re}\,s$'); ax.set_ylabel(r'$\mathrm{Im}\,s$')
    if title: ax.set_title(title)
    return ax

def show_routh(R, s):
    # display a Routh array as a LaTeX table
    n = len(R) - 1
    rows = [rf's^{{{n-i}}} & ' + ' & '.join(sp.latex(x) for x in r) for i, r in enumerate(R)]
    display(Math(r'\begin{array}{c|' + 'c'*len(R[0]) + r'}' + r' \\ '.join(rows) + r'\end{array}'))""")

md("## Routh array helper (handles the ε case and a row of zeros)")
code(routh_src)

md("## 4.2 Routh–Hurwitz\n### Example 4.2 — P control of 1/[(s+1)(s+2)(s+3)]")
code(r"""R = routh_array((s+3)*(s+2)*(s+1) + Kc, s, verbose=False)
show_routh(R, s)
sp.solve([r[0] > 0 for r in R], Kc)""")
md("### Special case 2 — Ex 4.2 at the ultimate gain $K_c=60$")
code(r"""R = routh_array((s+3)*(s+2)*(s+1) + 60, s, verbose=False)
show_routh(R, s)                     # the s^1 row was all zeros -> replaced by dA/ds
display(Math(r'A(s) = ' + sp.latex(sp.factor(6*s**2 + 66)) + r' = 0 \;\Rightarrow\; s = ' + sp.latex(sp.solve(6*sp.Symbol('s')**2 + 66))))  # s itself is declared real""")
md("### Special case 1 — zero in the first column")
code(r"""R = routh_array(s**4 + s**3 + 2*s**2 + 2*s + 3, s, verbose=False)
show_routh(R, s)                     # the zero in the s^2 row was replaced by epsilon
display(Math(r'\varepsilon\to0^+:\ ' + sp.latex([sp.limit(c, eps, 0, '+') for c in first_column(R)])))
print('roots:', np.roots([1, 1, 2, 2, 3]))""")
md("### Example 4.3 — PI control of 1/(s+1)²")
code(r"""tIp, Kcp = sp.symbols('tau_I K_c', positive=True)
R = routh_array(tIp*s*(s**2 + 2*s + 1) + Kcp*(tIp*s + 1), s, verbose=False)
show_routh(R, s)
boundary = sp.solve(sp.Eq(R[2][0], 0), tIp)[0]
boundary   # tau_I > Kc / (2 (1 + Kc))""")

md("## 4.3 Direct substitution\n### Example 4.2A")
code(r"""eq = sp.expand(((s+1)*(s+2)*(s+3) + Kc).subs(s, sp.I*w))
sp.solve([sp.re(eq), sp.im(eq)], [w, Kc], dict=True)""")
md("### Example 4.4 — dead time: exact vs. Padé")
code(r"""wu  = brentq(lambda w: 2*w + np.arctan(5*w) - np.pi, 0.1, 2.0)
Kcu = np.sqrt(1 + 25*wu**2)/0.8
print(f'exact : wu = {wu:.4f}, Kcu = {Kcu:.4f}')

G = ct.tf(0.8, [5, 1])
for order in (1, 3, 10):
    gm, pm, wcg, wcp = ct.margin(G*ct.tf(*ct.pade(2, order)))
    print(f'Pade {order:2d}: wu = {wcg:.4f}, Kcu = {gm:.4f}')""")
code(r"""t = np.linspace(0, 60, 3000)
fig, axs = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
for ax, order in zip(axs, (10, 1)):
    D = ct.tf(*ct.pade(2, order))
    for K in (5.0, 5.73, 6.5):
        _, y = ct.step_response(ct.feedback(K*G*D, 1), t)
        ax.plot(t, y, label=rf'$K_c={K}$')
    ax.set_ylim(-1.5, 2.5); ax.set_xlabel('time'); ax.legend()
    ax.set_title(r'exact delay $e^{-2s}$ (10th-order Padé)' if order == 10 else r'1st-order Padé $\dfrac{1-s}{1+s}$')
axs[0].set_ylabel(r'$c(t)$'); fig.tight_layout()""")
md("### Ultimate gain → Ziegler–Nichols settings")
code(r"""for name, Ku, wu_ in [('Ex 4.2', 60, np.sqrt(11)), ('Ex 4.4', Kcu, wu)]:
    Pu = 2*np.pi/wu_
    print(f'{name}: Kcu={Ku:.2f} Pu={Pu:.3f} | P: {0.5*Ku:.2f} | PI: {0.45*Ku:.2f}, {Pu/1.2:.3f} | '
          f'PID: {0.6*Ku:.2f}, {Pu/2:.3f}, {Pu/8:.3f}')""")

md("## 4.4 Root locus\n### Angle and magnitude conditions at $s=j\\sqrt{11}$ (Ex 4.2)")
code(r"""sp_ = 1j*np.sqrt(11); poles = np.array([-1, -2, -3])
print('sum of angles [deg]:', np.degrees(np.sum(np.angle(sp_ - poles))))
print('Kc = prod|s-p| =', np.prod(np.abs(sp_ - poles)))""")
md("### Example 4.2B")
code(r"""G42 = ct.tf(1, np.poly([-1, -2, -3]))
rlocus(G42, xlim=(-7, 1.5), ylim=(-5, 5), title=r'$1+K_c\dfrac{1}{(s+1)(s+2)(s+3)}=0$')
print('break-away candidates:', np.roots([3, 12, 11]))""")
md("### Example 4.6 — representative shapes")
code(r"""cases = [ct.tf(1, np.poly([-1, -2])), ct.tf(1, [1, 4, 5]),
         ct.tf([1, 2.5], np.poly([-1, -2])), ct.tf([1, 3], [1, 4, 5])]
names = [r'(a) $\dfrac{1}{(s+1)(s+2)}$', r'(b) $\dfrac{1}{s^2+4s+5}$',
         r'(c) $\dfrac{s+2.5}{(s+1)(s+2)}$', r'(d) $\dfrac{s+3}{s^2+4s+5}$']
fig, axs = plt.subplots(1, 4, figsize=(16, 4))
for ax, Gi, nm in zip(axs, cases, names):
    rlocus(Gi, xlim=(-6, 1), ylim=(-2.5, 2.5), ax=ax, title=nm)
fig.tight_layout()
P, Q = (s+2)*(s+1), s + sp.Rational(5, 2)
print('(c) break points:', sp.solve(sp.expand(Q*sp.diff(P, s) - P*sp.diff(Q, s)), s))
pz, p1, p2 = -3, -2+1j, -2-1j
print('(d) departure from -2-j [x pi]:', (np.angle(p2-pz) - np.angle(p2-p1) - np.pi)/np.pi)""")
md("### Effect of an added zero / pole")
code(r"""fig, axs = plt.subplots(1, 3, figsize=(15, 4))
den = np.poly([-1, -2, -3])
names = [r'no zero: $n-m=3$', r'zero at $-1.5$: $n-m=2$', r'zeros at $-1.5,\,-2.5$: $n-m=1$']
for ax, num, nm in zip(axs, ([1], [1, 1.5], np.poly([-1.5, -2.5])), names):
    rlocus(ct.tf(num, den), xlim=(-7, 1.5), ylim=(-6, 6), ax=ax, title=nm)
fig.tight_layout()""")
code(r"""# Example 4.3B: PI adds a pole at 0 and a zero at -1/tau_I
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
for ax, tau in zip(axs, (0.2, 0.6)):
    rlocus(ct.tf([tau, 1], tau*np.poly([0, -1, -1])), ax=ax, title=rf'$\tau_I={tau}$')
print('tau_I = 0.2 -> Kc,max =', 2*0.2/(1 - 2*0.2))""")
md("### RHP zero (inverse response)")
code(r"""Grhp = ct.tf([-1, 1], [2, 3, 1])
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
rlocus(Grhp, ax=axs[0], title=r'$1+K_c\dfrac{-s+1}{(s+1)(2s+1)}=0$')
t, y = ct.step_response(Grhp, np.linspace(0, 10, 400)); axs[1].plot(t, y)
axs[1].set_title('open-loop step: inverse response'); axs[1].set_xlabel('time'); axs[1].set_ylabel(r'$y(t)$')
fig.tight_layout()
for K in (2.9, 3.1):
    print(K, ct.feedback(K*Grhp, 1).poles())""")

md("## 4.5 Root-locus design\n### Example 4.7 — $\\zeta = 0.7$ with P control")
code(r"""G47 = ct.tf(1, np.polymul([2, 1], [4, 1]))
zeta = 0.7
Kc47 = 9/(8*zeta**2) - 1           # from zeta = 3/sqrt(8(1+Kc))
T = ct.feedback(Kc47*G47, 1)
print('Kc =', Kc47, ' poles:', T.poles()); print(ct.step_info(T)); print('offset =', 1/(1 + Kc47))
ax = rlocus(G47, xlim=(-0.8, 0.1), ylim=(-0.8, 0.8), zeta=0.7, title=r'$1+K_c\dfrac{1}{(2s+1)(4s+1)}=0$')
p = T.poles(); ax.plot(p.real, p.imag, 'rs'); ax.annotate(rf'$K_c={Kc47:.2f}$', (p.real[0], abs(p.imag[0])), xytext=(8, 4), textcoords='offset points', color='r');""")
md("### Example 4.8 — PI design")
code(r"""for tau in (3, sp.Rational(2, 3)):
    a2, a1, a0 = sp.Poly(sp.expand(tau*s*(2*s + 1) + sp.Rational(1, 2)*Kc*(tau*s + 1)), s).all_coeffs()
    sol = sp.solve(sp.Eq(a1**2, 4*sp.Rational(49, 100)*a2*a0), Kc)
    print('tau_I =', tau, '-> Kc for zeta=0.7:', [sp.N(x, 4) for x in sol if x.is_real])
for K in (0.5552, 7.2048):
    T = ct.feedback(ct.tf([K*0.5*2/3, K*0.5], np.polymul([2/3, 0], [2, 1])), 1)
    info = ct.step_info(T)
    print(f'Kc={K}: poles {np.round(T.poles(), 3)}, OS={info["Overshoot"]:.1f} %, ts={info["SettlingTime"]:.2f}')""")

md("## Problem #1 — (homework) start here")
code(r"""Gp1 = ct.tf([2, 2], np.polymul([1, 2, 0], [1, 0, 1]))
# (a) characteristic polynomial with Gc = Kc -> routh_array(...)
# (b) write Gc for PI and PD, then compare root-locus plots
""")

nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, Path(__file__).with_name("ch4_stability.ipynb"))
print("written", len(cells), "cells")
