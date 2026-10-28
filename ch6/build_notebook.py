"""Build the companion Colab notebook ch6_multiloop.ipynb."""
import nbformat as nbf
from pathlib import Path

blocks_src = Path(__file__).with_name("blocks.py").read_text()

cells = []
md = lambda t: cells.append(nbf.v4.new_markdown_cell(t))
code = lambda t: cells.append(nbf.v4.new_code_cell(t))

md("""# Ch.6 Multi-loop Systems — companion notebook
Process Dynamics and Control · SeoulTech

Python versions of every calculation and figure in the slides (`python-control`, `numpy`, `sympy`).
Loops with dead time are simulated **exactly** with the small block simulator below (no Padé approximation).""")
code(r"""%pip install -q control   # Colab: python-control is not preinstalled""")
code(r"""import numpy as np, sympy as sp, control as ct, matplotlib.pyplot as plt
from IPython.display import display, Math
plt.rcParams.update({'figure.dpi': 110, 'axes.grid': True, 'mathtext.fontset': 'cm'})
sp.init_printing()
s, Kc = sp.symbols('s K_c', positive=True)""")
md("## Block simulator with exact dead time (`blocks.py`)")
code(blocks_src)

md("## 6.1 Cascade control — Example 6.1\n### (a), (b) Effect of the slave gain $K_{c2}$")
code(r"""Kv, tv, KL = 0.5, 1.0, 0.75
for Kc2 in (2, 5, 18, 50):
    print(f'Kc2={Kc2:3d}: tau_v*={tv/(1+Kc2*Kv):.3f}  Kv*={Kc2*Kv/(1+Kc2*Kv):.3f}  KL*={KL/(1+Kc2*Kv):.3f}')
display(Math(r'\tau_v^* = 0.1\tau_v \Rightarrow K_{c2} = ' + sp.latex(sp.solve(sp.Eq(1/(1 + 0.5*Kc), sp.Rational(1, 10)), Kc)[0])))""")
code(r"""Gp, Gv, GL = ct.tf(0.8, [2, 1]), ct.tf(0.5, [1, 1]), ct.tf(0.75, [1, 1])
Kc2 = 18
Gv_s = ct.feedback(Kc2*Gv, 1)                       # 9/(s+10) = 0.9/(0.1s+1)
GL_s = ct.minreal(GL/(1 + Kc2*Gv), verbose=False)   # 0.75/(s+10)
print(Gv_s, GL_s)""")
md("### (d) Root loci of the master loop for $\\tau_I = 0.05,\\ 0.5,\\ 5$")
code(r"""fig, axs = plt.subplots(1, 3, figsize=(15, 4))
for ax, tI in zip(axs, (0.05, 0.5, 5)):
    L = ct.tf([tI, 1], [tI, 0]) * Gv_s * Gp
    ct.root_locus_plot(L, ax=ax); ax.set_aspect('auto')
    ax.set_xlim(-15, 10); ax.set_ylim(-20, 20); ax.set_title(rf'$\tau_I={tI}$')
    ax.set_xlabel(r'$\mathrm{Re}\,s$'); ax.set_ylabel(r'$\mathrm{Im}\,s$')
fig.tight_layout()
for tI in (0.05, 0.5, 5):
    a3, a2, a1, a0 = sp.Poly(sp.expand(tI*s*(sp.Rational(1, 10)*s + 1)*(2*s + 1) + sp.Rational(72, 100)*Kc*(tI*s + 1)), s).all_coeffs()
    display(Math(rf'\tau_I={tI}:\ a_2a_1-a_3a_0 = ' + sp.latex(sp.nsimplify(sp.expand(a2*a1 - a3*a0))) + r' > 0'))""")
md("### (e) Without the cascade, $\\tau_I = 0.5$")
code(r"""p = sp.expand(sp.Rational(1, 2)*s*(s + 1)*(2*s + 1) + sp.Rational(4, 10)*Kc*(sp.Rational(1, 2)*s + 1))
a3, a2, a1, a0 = sp.Poly(p, s).all_coeffs()
display(Math(sp.latex(p) + r' = 0')); sp.solve(a2*a1 - a3*a0 > 0, Kc)""")
md("### Load and set-point responses (replaces the Simulink runs)")
code(r"""Kc_, tI = 3, 0.5
Gc = ct.tf([Kc_*tI, Kc_], [tI, 0]); t = np.linspace(0, 30, 3001)
pairs = {'load step':      (ct.minreal(GL*Gp/(1 + Gc*Gv*Gp), verbose=False), ct.minreal(GL_s*Gp/(1 + Gc*Gv_s*Gp), verbose=False)),
         'set-point step': (ct.feedback(Gc*Gv*Gp, 1), ct.feedback(Gc*Gv_s*Gp, 1))}
fig, axs = plt.subplots(1, 2, figsize=(13, 4))
for ax, (name, (Tn, Tc)) in zip(axs, pairs.items()):
    yn, yc = ct.step_response(Tn, t).outputs, ct.step_response(Tc, t).outputs
    ax.plot(t, yn, 'r', label=f'single loop (peak {yn.max():.3f})')
    ax.plot(t, yc, 'b', label=rf'cascade $K_{{c2}}=18$ (peak {yc.max():.3f})')
    ax.set_title(name); ax.set_xlabel('time'); ax.legend()
axs[0].set_ylabel(r'$C(t)$'); fig.tight_layout()""")

md("## 6.2 Feedforward — Example 6.7: static vs. lead-lag compensation")
code(r"""GLd = ct.tf(1.2, [5, 1]); Gc = ct.tf([1.5, 3], [0.5, 0]); K_FF = -1.2/0.72
t = np.linspace(0, 20, 4001)
cases = {'feedback only': ct.tf(0, 1),
         rf'static $G_{{FF}}={K_FF:.2f}$': ct.tf(K_FF, 1),
         rf'lead-lag $G_{{FF}}={K_FF:.2f}\,\dfrac{{2s+1}}{{5s+1}}$': ct.tf([2*K_FF, K_FF], [5, 1])}
for name, Gff in cases.items():
    T = ct.minreal((GLd + Gff*Gv_s*Gp)/(1 + Gc*Gv_s*Gp), verbose=False)
    y = ct.step_response(T, t).outputs
    plt.plot(t, y, label=f'{name}  (IAE {np.trapezoid(abs(y), t):.3f})')
plt.xlabel('time'); plt.ylabel(r'$C(t)$'); plt.title('unit load step'); plt.legend();""")

md("## 6.5 Smith predictor — Example 6.8 (plant of Ex 4.4)")
code(r"""def smith(Kc, tI, use_predictor=True, theta_true=2.0, theta_model=2.0, tf=40):
    G, M0, Md, c = FOPDT(0.8, 5, theta_true), FOPDT(0.8, 5, 0.0), Delay(theta_model), PI(Kc, tI)
    y = ym0 = ymd = 0.0; out = []
    for k in range(int(tf/DT) + 1):
        u = c(1.0 - y - ((ym0 - ymd) if use_predictor else 0.0))
        y, ym0 = G(u), M0(u); ymd = Md(ym0); out.append(y)
    return np.arange(len(out))*DT, np.array(out)

fig, axs = plt.subplots(1, 2, figsize=(13, 4))
for args, lab in [((2.58, 5.85, False), r'ZN PI, no predictor'),
                  ((5, 5, False), r'$K_c=5$, no predictor'),
                  ((5, 5, True), r'$K_c=5$ + Smith predictor')]:
    axs[0].plot(*smith(*args), label=lab)
axs[0].set_ylim(-0.5, 2.5); axs[0].legend(); axs[0].set_title(r'$0.8e^{-2s}/(5s+1)$')
for th in (2.0, 2.6, 3.0):
    axs[1].plot(*smith(5, 5, True, theta_true=th), label=rf'true $\theta={th}$, model 2.0')
axs[1].legend(); axs[1].set_title('dead-time model error')
for a in axs: a.set_xlabel('time')
fig.tight_layout()""")

md("## 6.6 MIMO — process gain matrix and RGA\n### Example 6.3 – 6.5: blending")
code(r"""def rga(K):
    K = np.asarray(K, float)
    return K * np.linalg.inv(K).T            # Lambda = K o (K^-1)^T

for m1, m2 in ((0.1, 10), (9, 1)):
    F = m1 + m2
    K = np.array([[m2/F**2, -m1/F**2], [1, 1]])
    print(f'm1={m1}, m2={m2}:  x={m1/F:.4f}\nK =\n{K}\nLambda =\n{rga(K).round(4)}\n')""")
code(r"""m1, m2 = sp.symbols('m_1 m_2', positive=True)
x = m1/(m1 + m2)
lam = sp.simplify(sp.diff(x, m1) / (1/(m1 + m2)))     # (dx/dm1 at const m2) / (dx/dm1 at const F)
display(Math(r'\lambda_{x,m_1} = ' + sp.latex(lam) + r' = 1 - x'))
xx = np.linspace(0, 1, 101)
plt.plot(xx, 1 - xx, label=r'$\lambda_{x,m_1}$'); plt.plot(xx, xx, '--', label=r'$\lambda_{x,m_2}$')
plt.xlabel(r'$x$'); plt.ylabel('relative gain'); plt.legend();""")

md("## 6.7 Decoupling — Example 6.6: distillation column")
code(r"""K = np.array([[0.07, -0.05], [0.1, -0.15]])
print('RGA =\n', rga(K).round(3))
print('D12 = -K12/K11 =', -K[0, 1]/K[0, 0], '   D21 = -K21/K22 =', -K[1, 0]/K[1, 1])
itae = lambda Kp, tau, th: (0.586/Kp*(th/tau)**-0.916, tau/(1.03 - 0.165*th/tau))
(Kc1, tI1), (Kc2_, tI2) = itae(0.07, 12, 3), itae(-0.15, 10, 2)
print(f'ITAE: Kc1={Kc1:.1f}, tI1={tI1:.1f}   Kc2={Kc2_:.1f}, tI2={tI2:.1f}')""")
code(r"""G = [[(0.07, 12, 3), (-0.05, 15, 1)],
     [(0.10, 11, 4), (-0.15, 10, 2)]]
cases = {'no decoupling': (None, None),
         'static 0.71, 0.67': (0.714, 0.667),
         'dynamic (lead-lag + delay)': ((0.714, 12, 15, 0), (0.667, 10, 11, 2))}
fig, axs = plt.subplots(2, 2, figsize=(13, 6.5), sharex=True)
for col, (r1, r2) in enumerate([(1, 0), (0, 1)]):
    for name, (D12, D21) in cases.items():
        t, xD, xB, _, _ = simulate_2x2(G, (Kc1, Kc2_), (tI1, tI2), D12, D21, r1, r2, tf=80)
        axs[0, col].plot(t, xD, label=name); axs[1, col].plot(t, xB)
    axs[0, col].set_title(r'step in $x_D$ set point' if r1 else r'step in $x_B$ set point')
    axs[1, col].set_xlabel('time')
axs[0, 0].set_ylabel(r'$x_D$'); axs[1, 0].set_ylabel(r'$x_B$'); axs[0, 0].legend(); fig.tight_layout()""")

md("## Problem #1 — (homework) start here")
code(r"""G3 = [[(2, 10, 1), (1.5, 15, 1)],
      [(1.5, 15, 1), (2, 10, 1)]]
K3 = np.array([[g[0] for g in row] for row in G3])
# (a) rga(K3) ...   (b) decouplers ...   (c) simulate_2x2(G3, Kc, tI, D12, D21, r1=1, r2=0)
""")

nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, Path(__file__).with_name("ch6_multiloop.ipynb"))
print("written", len(cells), "cells")
