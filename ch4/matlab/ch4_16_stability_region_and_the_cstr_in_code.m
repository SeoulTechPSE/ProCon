%% Ch.4 — Stability region and the CSTR in code
% Process Dynamics and Control, SeoulTech — slide 17
% https://seoultechpse.github.io/ProCon/ch4/ch4_stability.html#/3/10
% Requires: Control System Toolbox

clear; close all; clc

% stability boundary of PI on 1/((s+1)(s+2)(s+3))
Kc = linspace(0.1, 59.9, 300);
tImin = 36*Kc./(360 + 54*Kc - Kc.^2);
area(Kc, tImin), axis([0 65 0 10]), xlabel('K_c'), ylabel('\tau_I')

for pt = [10 1; 10 0.3; 30 3; 45 3]'
    p = roots([pt(2) 6*pt(2) 11*pt(2) pt(2)*(6 + pt(1)) pt(1)]);
    fprintf('Kc = %g, tauI = %g: max Re = %.3f\n', pt(1), pt(2), max(real(p)))
end

% CSTR, upper steady state
G = tf([2.092 10.02], [1 -2.715 4.215]);
pole(G)                                     % 1.36 +- 1.54j: open-loop unstable
for k = [1 1.3 3], pole(feedback(k*G, 1)), end
