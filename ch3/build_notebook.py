"""Build the companion Colab notebook ch3_tuning.ipynb."""
import nbformat as nbf
from pathlib import Path

tuning_src = Path(__file__).with_name("tuning.py").read_text()

cells = []
md = lambda t: cells.append(nbf.v4.new_markdown_cell(t))
code = lambda t: cells.append(nbf.v4.new_code_cell(t))

md("""# Ch.3 Tuning of Single-Loop Control Systems — companion notebook
Process Dynamics and Control · SeoulTech

Python versions of every calculation and figure in the slides (`python-control`, `numpy`, `sympy`).""")
code(r"""%pip install -q control   # Colab: python-control is not preinstalled""")
code(r"""import numpy as np, sympy as sp, control as ct, matplotlib.pyplot as plt
from IPython.display import display, Math
plt.rcParams.update({'figure.dpi': 110, 'axes.grid': True, 'mathtext.fontset': 'cm'})
sp.init_printing()
step = lambda sysm, t: np.asarray(ct.step_response(sysm, t).outputs, float).ravel()""")
md("## Tuning relations (`tuning.py`)")
code(tuning_src)

md("## 3.1 Empirical tuning\n### Fitting a FOPDT model to a process-reaction curve")
code(r"""G = ct.tf(1, np.polymul(np.polymul([2, 1], [1, 1]), [0.5, 1]))     # 'true' process of Ex 3.6
t = np.linspace(0, 30, 30001); y = step(G, t)
K, tau, theta = fit_two_point(t, y);  Kt, taut, thetat = fit_tangent(t, y)
print(f'two-point: K={K:.3f}, tau={tau:.3f}, theta={theta:.3f}')
print(f'tangent  : K={Kt:.3f}, tau={taut:.3f}, theta={thetat:.3f}')
fopdt = lambda K, tau, th: np.where(t < th, 0, K*(1 - np.exp(-(t - th)/tau)))
plt.plot(t, y, 'k', lw=2, label='measured')
plt.plot(t, fopdt(K, tau, theta), '--', label='two-point fit')
plt.plot(t, fopdt(Kt, taut, thetat), ':', label='tangent fit')
plt.xlim(0, 16); plt.xlabel('time'); plt.legend();""")
md("### Error integrals")
code(r"""tt = np.linspace(0, 12, 3000)
e = 1 - step(ct.feedback(pid_tf(2.03, 3.76)*G, 1), tt)
for name, w in [('ISE', e**2), ('IAE', abs(e)), ('ITAE', tt*abs(e))]:
    print(f'{name:4s} = {np.trapezoid(w, tt):.3f}')""")
md("### Ziegler–Nichols ultimate cycle — Van de Vusse reactor")
code(r"""Gvv = ct.tf(0.5858*np.array([-0.3549, 1]), [0.1858, 0.8627, 1])
Kcu, _, wu, _ = ct.margin(Gvv); Tu = 2*np.pi/wu
print(f'Kcu = {Kcu:.4f},  wu = {wu:.4f},  Tu = {Tu:.4f}')
t = np.linspace(0, 8, 4001)
for Kc in (1, 2, 3, 4, Kcu):
    plt.plot(t, step(ct.feedback(Kc*Gvv, 1), t), label=rf'$K_c={Kc:.3g}$')
plt.legend(); plt.xlabel('time'); plt.title(r'P control: $K_c \to K_{cu}$');""")
code(r"""t = np.linspace(0, 5, 2001)
fig, axs = plt.subplots(1, 2, figsize=(13, 4))
for name, pars in {'P': (0.5*Kcu,), 'PI': (0.455*Kcu, 0.833*Tu), 'PID': (0.6*Kcu, 0.5*Tu, 0.125*Tu)}.items():
    axs[0].plot(t, step(ct.feedback(pid_tf(*pars)*Gvv, 1), t), label=name)
    print(name, np.round(pars, 3))
for name, k, d in [('quarter decay', 0.6, 0.125), ('some overshoot', 0.33, 1/3), ('no overshoot', 0.2, 1/3)]:
    axs[1].plot(t, step(ct.feedback(pid_tf(k*Kcu, 0.5*Tu, d*Tu)*Gvv, 1), t), label=f'PID, {name}')
for a in axs: a.legend(); a.set_xlabel('time'); a.set_ylim(-1, 1.5)""")

md("### Example 3.6 — five tuning rules on the same plant")
code(r"""tl = np.linspace(0, 40, 20001)
print(f'{"":4s}{"rule":24s}{"Kc":>7s}{"tI":>7s}{"tD":>7s}{"OS%":>7s}{"IAEsp":>8s}{"IAEld":>8s}{"GM":>7s}{"PM":>6s}')
for ctrl in ('PI', 'PID'):
    for name, rule in RULES.items():
        Kc, tI, tD = rule(ctrl, K, tau, theta); C = pid_tf(Kc, tI, tD)
        ys, yl = step(ct.feedback(C*G, 1), tl), step(ct.feedback(G, C), tl)
        gm, pm, *_ = ct.margin(C*G)
        print(f'{ctrl:4s}{name:24s}{Kc:7.2f}{tI:7.2f}{tD:7.2f}{(ys.max()-1)*100:7.1f}'
              f'{np.trapezoid(abs(1-ys), tl):8.2f}{np.trapezoid(abs(yl), tl):8.2f}{gm:7.1f}{pm:6.0f}')""")
code(r"""t = np.linspace(0, 25, 5001)
fig, axs = plt.subplots(2, 2, figsize=(13, 7), sharex=True)
for col, ctrl in enumerate(('PI', 'PID')):
    for name, rule in RULES.items():
        C = pid_tf(*rule(ctrl, K, tau, theta))
        axs[0, col].plot(t, step(ct.feedback(C*G, 1), t), label=name)
        axs[1, col].plot(t, step(ct.feedback(G, C), t))
    axs[0, col].set_title(f'{ctrl}: set-point step'); axs[1, col].set_title(f'{ctrl}: load step')
axs[0, 0].legend(fontsize=9); fig.tight_layout()""")

md("## 3.2 Direct synthesis and IMC\n### Examples 3.1–3.4 with sympy")
code(r"""s, Kp, tp, t1, t2, tc, th, z, tau_ = sp.symbols('s K_p tau_p tau_1 tau_2 tau_c theta zeta tau', positive=True)
ds = lambda Gp, CR: sp.factor(sp.simplify(1/Gp * CR/(1 - CR)))
display(Math(r'\text{Ex 3.1: } G_c = ' + sp.latex(ds(Kp/(tp*s + 1), 1/(tc*s + 1)))))
display(Math(r'\text{Ex 3.2: } G_c = ' + sp.latex(ds(Kp/((t1*s + 1)*(t2*s + 1)), 1/(tc*s + 1)))))
# Ex 3.3: e^{-theta s} cancels; denominator (tc s + 1) - e^{-theta s} ~ (tc + theta) s
display(Math(r'\text{Ex 3.3: } G_c \approx ' + sp.latex(sp.factor((tp*s + 1)/Kp / ((tc + th)*s)))))
display(Math(r'\text{Ex 3.4: } G_c = ' + sp.latex(ds(Kp/((t1*s + 1)*(t2*s + 1)), 1/(tau_**2*s**2 + 2*z*tau_*s + 1)))))""")
md("### Example 3.5 — IMC for a FOPDT model gives an ideal PID")
code(r"""Gm = Kp/((tp*s + 1)*(th/2*s + 1)); Gplus = -th/2*s + 1        # 1st-order Pade split
Q = 1/Gm/(tc*s + 1)                                              # model controller, r = 1
Gc = sp.factor(sp.simplify(Q/(1 - Q*Gm*Gplus)))
display(Math('G_c = ' + sp.latex(Gc)))
Kc_ = (2*tp/th + 1)/(Kp*(2*tc/th + 1)); tI_ = tp + th/2; tD_ = tp/(2*tp/th + 1)
print('equals ideal PID with the slide formulas:', sp.simplify(Gc - Kc_*(1 + 1/(tI_*s) + tD_*s)) == 0)""")
md("### Choosing $\\tau_c$")
code(r"""t = np.linspace(0, 20, 4001)
for f in (0.5, 1.0, 2.0):
    pars = imc('PID', K, tau, theta, f*theta)
    plt.plot(t, step(ct.feedback(pid_tf(*pars)*G, 1), t), label=rf'$\tau_c={f}\theta$, $K_c={pars[0]:.2f}$')
plt.legend(); plt.xlabel('time');
# IMC-PI on an exact FOPDT: loop = e^{-theta s}/(2 theta s) for tau_c = theta  ->  GM = pi, PM = 61 deg
w = np.pi/2/theta; print('GM =', 1/abs(np.exp(-1j*w*theta)/(2*theta*1j*w)),
                         ' PM =', 180 + np.degrees(-np.pi/2 - 1/(2*theta)*theta))""")
md("### Example 3.7 — IMC for the Van de Vusse reactor")
code(r"""tcv = sp.symbols('tau_c', positive=True)
Gm_vv = sp.Rational(5858, 10000)/(sp.Rational(1858, 10000)*s**2 + sp.Rational(8627, 10000)*s + 1)
Gplus_vv = -sp.Rational(3549, 10000)*s + 1
Q = 1/Gm_vv/(tcv*s + 1)**2                                       # r = 2 (relative degree 2)
display(Math('G_c = ' + sp.latex(sp.factor(sp.simplify(Q/(1 - Q*Gm_vv*Gplus_vv))))))
t = np.linspace(0, 5, 5001)
for tc_ in (0.15, 0.3):
    y = step(ct.tf([-0.3549, 1], np.polymul([tc_, 1], [tc_, 1])), t)
    plt.plot(t, y, label=rf'IMC $\tau_c={tc_}$ (min {y.min():.2f})')
plt.plot(t, step(ct.feedback(pid_tf(0.6*Kcu, 0.5*Tu, 0.125*Tu)*Gvv, 1), t), '--', label='ZN PID')
plt.legend(); plt.xlabel('time');""")

md("## Problem #1 — (homework) start here")
code(r"""t_min = np.arange(13)
T2m = np.array([12.0, 12.0, 12.5, 13.1, 14.0, 14.8, 15.4, 16.1, 16.4, 16.8, 16.9, 17.0, 16.9])   # mA
dPs = 20 - 18                                    # psig step in steam pressure
# 1) convert the step to the controller-output scale (K_v = 0.9 psi/psi, K_IP = 0.75 psi/mA)
# 2) fit a FOPDT model (fit_two_point), 3) apply imc(...) and itae(..., mode='sp' / 'load')
""")

nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, Path(__file__).with_name("ch3_tuning.ipynb"))
print("written", len(cells), "cells")
