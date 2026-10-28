"""Build the companion Colab notebook ch5_frequency.ipynb."""
import nbformat as nbf
from pathlib import Path

cells = []
md = lambda t: cells.append(nbf.v4.new_markdown_cell(t))
code = lambda t: cells.append(nbf.v4.new_code_cell(t))

md("""# Ch.5 Frequency-Response Analysis & Design — companion notebook
Process Dynamics and Control · SeoulTech

Python versions of every calculation and figure in the slides (`python-control`, `numpy`, `scipy`).""")
code("""%pip install -q control   # Colab: python-control is not preinstalled""")
code("""import numpy as np, control as ct, matplotlib.pyplot as plt
from scipy.optimize import brentq
plt.rcParams.update({'figure.dpi': 110, 'axes.grid': True})

def fr(G, w, delay=0.0):
    # G(jw) e^{-jw delay}: magnitude and unwrapped phase (deg)
    g = G(1j*w) * np.exp(-1j*w*delay)
    return g, np.abs(g), np.degrees(np.unwrap(np.angle(g)))

def bode(G, w, delay=0.0, axs=None, **kw):
    if axs is None:
        _, axs = plt.subplots(2, 1, sharex=True, figsize=(7, 5))
    _, m, p = fr(G, w, delay)
    axs[0].loglog(w, m, **kw); axs[1].semilogx(w, p, **kw)
    axs[0].set_ylabel('AR'); axs[1].set_ylabel('phase (deg)'); axs[1].set_xlabel('ω')
    return axs""")

md("## 5.1 A sine in, a sine out — $G=2/(1.5s+1)$")
code("""G = ct.tf(2, [1.5, 1])
t = np.linspace(0, 15, 6000)
fig, axs = plt.subplots(1, 2, figsize=(13, 3.5))
for ax, w in zip(axs, (3, 10)):
    _, y = ct.forced_response(G, t, np.sin(w*t))
    ax.plot(t, np.sin(w*t), label='u'); ax.plot(t, y, label='y'); ax.set_xlim(0, 8 if w == 3 else 4)
    g = complex(G(1j*w))
    ax.set_title(f'ω={w}: AR={abs(g):.3f}, φ={np.degrees(np.angle(g)):.1f}°'); ax.legend()""")
md("### Example 5.1 — magnitude and phase of $(\\tau_as+1)/[(\\tau_1s+1)(\\tau_2s+1)]$")
code("""ta, t1, t2 = 5, 10, 2
G = ct.tf([ta, 1], np.polymul([t1, 1], [t2, 1]))
w = 0.3
print('direct    :', abs(G(1j*w)), np.degrees(np.angle(G(1j*w))))
print('formula   :', np.sqrt(1+(w*ta)**2)/np.sqrt(1+(w*t1)**2)/np.sqrt(1+(w*t2)**2),
      np.degrees(np.arctan(w*ta) - np.arctan(w*t1) - np.arctan(w*t2)))""")

md("## 5.2 Bode and Nyquist plots\n### Example 5.2 — first order")
code("""G = ct.tf(1, [2, 1])
ct.bode_plot(G, dB=False, deg=True); plt.show()
ct.nyquist_plot(G); plt.show()""")
md("### Example 5.3 — second order, $\\zeta = 1.2 \\dots 0.2$")
code("""tau, w = 2, np.logspace(-2, 2, 800)
axs = None
for z in (1.2, 1.0, 0.8, 0.6, 0.4, 0.2):
    axs = bode(ct.tf(1, [tau**2, 2*z*tau, 1]), w, axs=axs, label=f'ζ={z}')
axs[0].legend(ncol=2)
for z in (0.2, 0.4, 0.6):
    print(f'ζ={z}: ωr·τ={np.sqrt(1-2*z*z):.3f}, Mpω/K={1/(2*z*np.sqrt(1-z*z)):.3f}')""")
md("### Examples 5.4–5.8 — lead, dead time, FOPDT, integrator, lag + integrator")
code("""w = np.logspace(-2, 1.5, 2000)
fig, axs = plt.subplots(2, 5, figsize=(18, 5.5), sharex=True)
cases = [(ct.tf([2, 1], 1), 0, 'lead 2s+1'), (ct.tf(1, 1), 2, 'e^{-2s}'),
         (ct.tf(1, [10, 1]), 2, 'e^{-2s}/(10s+1)'), (ct.tf(1, [1, 0]), 0, '1/s'),
         (ct.tf(1, [2, 1, 0]), 0, '1/[s(2s+1)]')]
for j, (G, d, name) in enumerate(cases):
    bode(G, w, d, axs=axs[:, j]); axs[0, j].set_title(name)""")
code("""# Nyquist of the FOPDT: a spiral into the origin
g, _, _ = fr(ct.tf(1, [10, 1]), np.logspace(-3, 1.5, 6000), 2.0)
plt.plot(g.real, g.imag); plt.plot(-1, 0, 'r+', ms=12); plt.axis('equal'); plt.title('Ex 5.6 Nyquist');""")
md("### Example 5.9 — asymptotic sketch vs exact")
code("""G = ct.tf([5, 1], np.polymul([10, 1], [2, 1])); w = np.logspace(-3, 1, 600)
_, m, p = fr(G, w)
asym = (-20*np.log10(np.maximum(w/0.1, 1)) + 20*np.log10(np.maximum(w/0.2, 1))
        - 20*np.log10(np.maximum(w/0.5, 1)))
plt.semilogx(w, 20*np.log10(m), label='exact'); plt.semilogx(w, asym, '--', label='asymptotes')
plt.ylabel('dB'); plt.legend()
print('largest error (dB):', np.max(np.abs(20*np.log10(m) - asym)))""")

md("## 5.3 Stability analysis\n### Examples 5.10, 5.11 — inverse-response process with P control")
code("""G = ct.tf([-6, 3], np.polymul([10, 1], [5, 1]))
gm, pm, wc, wg = ct.margin(G)                       # Kc = 1
print(f'|G(jωc)| = {1/gm:.3f} at ωc = {wc:.3f}  ->  Ku = {gm:.3f}, Pu = {2*np.pi/wc:.2f} s')
print('Routh:  50 s^2 + (15-6Kc) s + (1+3Kc)  ->  Ku = 2.5, ω = ', np.sqrt(8.5/50))
t = np.linspace(0, 100, 3000)
for K in (0.5, 1.5, 2.5):
    _, y = ct.step_response(ct.feedback(K*G, 1), t); plt.plot(t, y, label=f'Kc={K}')
plt.legend(); plt.xlabel('time (s)');""")
code("""ct.nyquist_plot(G); plt.xlim(-1.5, 3.2); plt.show()""")
md("### Ex 4.4 revisited — dead time by Bode, exactly")
code("""G44 = ct.tf(0.8, [5, 1])
wc = brentq(lambda w: np.arctan(5*w) + 2*w - np.pi, 0.1, 2)
print('ωc =', wc, ' Kcu =', 1/abs(G44(1j*wc)))""")
md("### Example 5.14 — Nyquist for an open-loop unstable process $K_c/(s-1)$")
code("""w = np.logspace(-3, 3, 4000)
fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, K in zip(axs, (0.5, 2.0)):
    g = K/(1j*w - 1)
    ax.plot(g.real, g.imag, 'b', g.real, -g.imag, 'b--'); ax.plot(-1, 0, 'r+', ms=14)
    ax.set_aspect('equal'); ax.set_title(f'Kc={K}: closed-loop pole at s = {1-K:+.1f}')""")
md("### Gain and phase margins — Example 5.12 (Ziegler–Nichols PI)")
code("""Ku, Pu = 2.5, 2*np.pi/np.sqrt(8.5/50)
Kc, tI = Ku/2.2, Pu/1.2
L = Kc*ct.tf([tI, 1], [tI, 0])*G
gm, pm, wc, wg = ct.margin(L)
print(f'Kc={Kc:.3f}, τI={tI:.2f}:  GM={gm:.3f}, PM={pm:.1f}°, ωc={wc:.3f}, ωg={wg:.3f}')
print('extra dead time that destabilizes: θmax = PM[rad]/ωg =', np.radians(pm)/wg, 's')
ct.bode_plot(L, display_margins=True); plt.show()
T = ct.feedback(L, 1); U = ct.feedback(Kc*ct.tf([tI, 1], [tI, 0]), G)
t = np.linspace(0, 120, 3000)
plt.plot(t, ct.step_response(T, t)[1], label='y'); plt.plot(t, ct.step_response(U, t)[1], label='u'); plt.legend()
print(ct.step_info(T))""")
md("### Phase margin vs damping ratio")
code("""z = np.linspace(0.02, 1, 200)
pm = np.degrees(np.arctan(2*z/np.sqrt(np.sqrt(1+4*z**4) - 2*z**2)))
plt.plot(z, pm, label='exact'); plt.plot(z, 100*z, '--', label='100 ζ'); plt.xlabel('ζ'); plt.ylabel('PM (deg)'); plt.legend();""")

md("## 5.4 Controller design\n### Example 5.13 — retune for GM ≥ 2 and PM ≥ 45° with the $G^*$ Bode plot")
code("""Gs = ct.tf([tI, 1], [tI, 0])*G                 # G* = everything except Kc
Kcu = ct.margin(Gs)[0]
w = np.logspace(-3, 1, 100000); g = Gs(1j*w); ph = np.degrees(np.unwrap(np.angle(g)))
i = np.argmin(abs(ph + 135))
Kc_GM, Kc_PM = Kcu/2, 1/abs(g[i])
print(f'Kcu={Kcu:.3f}  Kc(GM=2)={Kc_GM:.3f}  Kc(PM=45°)={Kc_PM:.3f} at ωg={w[i]:.3f}')
t = np.linspace(0, 120, 3000)
for K in (Kc, Kc_GM, Kc_PM):
    m = ct.margin(K*Gs); info = ct.step_info(ct.feedback(K*Gs, 1))
    print(f'Kc={K:.3f}: GM={m[0]:.2f} PM={m[1]:.1f}°  overshoot={info["Overshoot"]:.0f} %  ts={info["SettlingTime"]:.0f} s')
    plt.plot(t, ct.step_response(ct.feedback(K*Gs, 1), t)[1], label=f'Kc={K:.2f}')
plt.legend();""")

md("## Problem #2 — (homework) start here\n$G_p = 2e^{-s}/(10s+1)$, PI with $\\tau_I = 10$")
code("""Gp = ct.tf(2, [10, 1]); theta = 1.0; tI = 10
w = np.logspace(-3, 2, 20000)
g_star = Gp(1j*w)*np.exp(-1j*w*theta)*(1 + 1/(1j*w*tI))      # G*(jω)
# (b), (c): find ωc, Kcu and the Kc for PM = 45° from g_star
""")

nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, Path(__file__).with_name("ch5_frequency.ipynb"))
print("written", len(cells), "cells")
