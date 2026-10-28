"""Build the companion Colab notebook ch1_dynamics.ipynb."""
import nbformat as nbf
from pathlib import Path

cells = []
md = lambda t: cells.append(nbf.v4.new_markdown_cell(t))
code = lambda t: cells.append(nbf.v4.new_code_cell(t))

md("""# Ch.1 Mathematical Preliminaries and Dynamic Response — companion notebook
Process Dynamics and Control · SeoulTech

Python versions of every transform (`sympy`), calculation and figure in the slides (`python-control`, `numpy`).""")
code(r"""%pip install -q control   # Colab: python-control is not preinstalled""")
code(r"""import numpy as np, sympy as sp, control as ct, matplotlib.pyplot as plt
from IPython.display import display, Math
plt.rcParams.update({'figure.dpi': 110, 'axes.grid': True, 'mathtext.fontset': 'cm'})
step = lambda G, t: np.asarray(ct.step_response(G, t).outputs, float).ravel()
imp  = lambda G, t: np.asarray(ct.impulse_response(G, t).outputs, float).ravel()
s, t = sp.symbols('s t'); tp = sp.Symbol('t', positive=True)
show = lambda lhs, e: display(Math(lhs + ' = ' + sp.latex(e)))""")

md("## 1.1 Linearization\n### Example 1.1 — mixed vessel $V\\,dc/dt = q c_i - q c$")
code(r"""V, q, ci, c = sp.symbols('V q c_i c', positive=True)
qs, cis, cs = sp.symbols('q_s c_{is} c_s', positive=True)
dq, dci, dc = sp.symbols("q' c_i' c'")
f = (q*ci - q*c)/V
lin = sum(sp.diff(f, v).subs({q: qs, ci: cis, c: cs})*d for v, d in [(q, dq), (ci, dci), (c, dc)])
show(r"\frac{dc'}{dt}", sp.expand(lin))
show(r"\text{with } c_s = c_{is}", sp.expand(lin.subs(cs, cis)))""")
md("### Example 1.3 — CSTR, $C_A'(s)/T_c'(s)$")
code(r"""a11, a12, a21, a22, b2 = sp.symbols('a_{11} a_{12} a_{21} a_{22} b_2')
A = sp.Matrix([[a11, a12], [a21, a22]]); B = sp.Matrix([0, b2])
X = (s*sp.eye(2) - A).inv()*B
show(r"\frac{C_A'}{T_c'}", sp.factor(sp.simplify(X[0])))
show(r"\frac{T'}{T_c'}", sp.factor(sp.simplify(X[1])))""")

md("## 1.2 Laplace transforms")
code(r"""a, w = sp.symbols('a omega', positive=True)
for f in [sp.S(1), sp.exp(-a*tp), tp, sp.sin(w*tp), sp.cos(w*tp), sp.exp(-a*tp)*sp.sin(w*tp)]:
    show(r'\mathcal{L}[' + sp.latex(f) + ']', sp.laplace_transform(f, tp, s, noconds=True))""")
md("### Example 1.4 — final-value theorem (only if all poles of $sF$ are in the LHP)")
code(r"""for F in [6*(s - 2)*(s + 2)/(s*(s + 1)*(s + 3)*(s + 4)), 1/(s - 2), 6*(s + 3)/(s**3 + s**2 - 4*s - 4)]:
    poles = sp.solve(sp.denom(sp.together(s*F)), s)
    ok = all(sp.re(p) < 0 for p in poles)
    print(f'{str(F):40s} lim sF = {sp.limit(s*F, s, 0)}   poles of sF {poles}  ->', 'valid' if ok else 'NOT valid')""")

md("## 1.3 Partial fractions — Examples 1.5–1.7")
code(r"""for F in [(6*s**2 - 12)/(s**3 + s**2 - 4*s - 4), 6*s/(s**3 + s**2 - 4*s - 4), 6/((s + 1)*(s + 2)*(s + 3)),
          (s + 5)/(s**2 + 4*s + 13), 2/((s + 1)**3*(s + 2))]:
    display(Math(sp.latex(F) + ' = ' + sp.latex(sp.apart(F, s)) + r'\;\Rightarrow\; f(t) = '
                 + sp.latex(sp.simplify(sp.inverse_laplace_transform(F, s, tp)))))""")
code(r"""import scipy.signal as sig
r, p, k = sig.residue([6, 0, -12], [1, 1, -4, -4])
print('residues', np.round(r, 4), ' poles', np.round(p, 4))
tt = np.linspace(0, 1.5, 300)
for y, lab in [(2*np.exp(-tt), '2e^{-t}'), (3*np.exp(-2*tt), '3e^{-2t}'), (np.exp(2*tt), 'e^{2t}')]:
    plt.plot(tt, y, label=f'${lab}$')
plt.legend(); plt.xlabel('t');""")

md("## 1.4 Poles shape the response")
code(r"""tt = np.linspace(0, 10, 1000)
for re, im in [(-0.5, 0), (-2, 0), (-0.5, 2.5), (0, 2.5), (0.15, 2.5), (0.2, 0)]:
    plt.plot(tt, np.exp(re*tt)*(np.cos(im*tt) if im else 1), label=f'{re} ± {im}j' if im else f'{re}')
plt.ylim(-2.5, 2.5); plt.legend(ncol=3); plt.xlabel('t');""")

md("## 1.5 First-order systems")
code(r"""tt = np.linspace(0, 12, 1201)
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
for tau in (2, 1, 0.5, 0.25):
    G = ct.tf(1, [tau, 1]); axs[0].plot(tt, step(G, tt), label=f'tau={tau}'); axs[1].plot(tt, imp(G, tt), label=f'tau={tau}')
axs[0].set_title('step'); axs[1].set_title('impulse'); [a.legend() for a in axs];
print('1 - e^-n :', np.round(1 - np.exp(-np.arange(1, 6)), 4))""")
md("### Example 1.8 — two tanks in series, pulse vs impulse (pulse length 0.25 min)")
code(r"""tt = np.linspace(0, 15, 15001); G1, G2 = ct.tf(1, [2, 1]), ct.tf(1, [1.5, 1])
u = np.where(tt < 0.25, 5.0, 0.0)
plt.plot(tt, ct.forced_response(G1*G2, tt, u).outputs + 1, label='c2, pulse')
plt.plot(tt, 1.25*imp(G1*G2, tt) + 1, '--', label='c2, impulse 1.25 delta')
plt.plot(tt, ct.forced_response(G1, tt, u).outputs + 1, label='c1, pulse')
plt.legend(); plt.xlabel('time (min)');""")

md("## 1.6 Second-order systems")
code(r"""tt = np.linspace(0, 20, 2001)
for z in (0.2, 0.4, 0.6, 0.8, 1, 2):
    plt.plot(tt, step(ct.tf(1, [1, 2*z, 1]), tt), label=f'zeta={z}')
plt.legend(); plt.xlabel('t/tau');
z = 0.3; info = ct.step_info(ct.tf(1, [1, 2*z, 1]), SettlingTimeThreshold=0.02)
OS = np.exp(-np.pi*z/np.sqrt(1 - z**2))
print(f"OS {info['Overshoot']:.1f}% (theory {100*OS:.1f}%), tp {info['PeakTime']:.3f} (theory {np.pi/np.sqrt(1 - z**2):.3f}), DR {OS**2:.3f}")""")
md("### Example 1.9 — manometer: critical radius")
code(r"""mu, rho, L, g, R = sp.symbols('mu rho L g R', positive=True)
wn = sp.sqrt(3*g/(2*L)); zeta = 6*mu/(R**2*rho)/(2*wn)
Rcr = sp.solve(sp.Eq(zeta, 1), R)[0]
show('R_{cr}^4', sp.simplify(Rcr**4))
print('water, L = 1 m:', float(Rcr.subs({mu: 1e-3, rho: 1000, L: 1, g: 9.81}))*1000, 'mm')""")

md("## 1.7 Dead time — Example 1.10, Padé approximations")
code(r"""tt = np.linspace(0, 50, 5001); G = ct.tf(1, [10, 1])
ye = np.interp(tt - 3, tt, step(G, tt), left=0)
plt.plot(tt, ye, 'k', lw=2, label='exact')
for n in (1, 2):
    num, den = ct.pade(3, n); print(n, ct.tf(num, den))
    plt.plot(tt, step(G*ct.tf(num, den), tt), '--', label=f'{n}/{n} Pade')
plt.legend(); plt.xlim(0, 15);""")

md("## 1.8 Higher order — Example 1.11, low-order approximations")
code(r"""G = ct.tf(3, np.polymul(np.polymul([0.1, 1], [0.5, 1]), np.polymul([1, 1], [3, 1])))
tt = np.linspace(0, 15, 3001); y = step(G, tt); plt.plot(tt, y, 'k', lw=3, label='full')
for lab, den, th in [('FOPDT', [3, 1], 1.6), ('SOPDT', np.polymul([1, 1], [3, 1]), 0.6),
                     ('FOPDT half rule', [3.5, 1], 1.1), ('SOPDT half rule', np.polymul([1.25, 1], [3, 1]), 0.35)]:
    ya = np.interp(tt - th, tt, step(ct.tf(3, den), tt), left=0)
    plt.plot(tt, ya, '--', label=f'{lab}: IAE {np.trapezoid(abs(ya - y), tt):.2f}')
plt.legend();""")
md("### Interacting tanks")
code(r"""A1, A2, R1, R2 = sp.symbols('A_1 A_2 R_1 R_2', positive=True); H1, H2, Q = sp.symbols('H_1 H_2 Q')
sol = sp.solve([A1*s*H1 - (Q - (H1 - H2)/R1), A2*s*H2 - ((H1 - H2)/R1 - H2/R2)], [H1, H2])
show(r'\frac{H_2}{Q_i}', sp.factor(sol[H2]/Q)); show(r'\frac{H_1}{Q_i}', sp.factor(sol[H1]/Q))
tt = np.linspace(0, 20, 2001)
plt.plot(tt, step(ct.tf(1, [1, 2, 1]), tt), label='non-interacting'); plt.plot(tt, step(ct.tf(1, [1, 3, 1]), tt), label='interacting')
plt.legend();""")

md("## 1.9 Zeros — lead-lag and parallel elements")
code(r"""tt = np.linspace(0, 18, 1801)
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
for tz in (4, 2, 1, 0, -1):
    axs[0].plot(tt, step(ct.tf([tz, 1], [2, 1]), tt), label=f'tau_z={tz}')
for t1, t2 in [(2, 2), (2, 0.5), (0.5, 2)]:
    axs[1].plot(tt, step(ct.tf(3, [t1, 1]) + ct.tf(-1, [t2, 1]), tt), label=f'tau1={t1}, tau2={t2}')
[a.legend() for a in axs];""")

md("## Problems — (homework) start here")
code(r"""# Problem #6: tank (2 m^3) + pipe as 5 tanks of 0.02 m^3 each, q = 1 m^3/min
G_full = ct.tf(1, [2, 1])*ct.tf(1, [0.02, 1])**5
# compare with a low-order approximation of your choice
""")

nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, Path(__file__).with_name("ch1_dynamics.ipynb"))
print("written", len(cells), "cells")
