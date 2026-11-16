%% Ch.5 — Maximum sensitivity and bandwidth in code
% Process Dynamics and Control, SeoulTech — slide 36
% https://seoultechpse.github.io/ProCon/ch5/ch5_frequency.html#/5/6
% Requires: Control System Toolbox

clear; close all; clc

G = tf([-6 3], conv([10 1], [5 1]));
[Ku, ~, wc] = margin(G);  tI = 2*pi/wc/1.2;              % ZN tauI = 12.7
for Kc = [Ku/2.2 0.93 0.60]
    L = Kc*tf([tI 1], [tI 0])*G;
    S = feedback(1, L);  T = feedback(L, 1);
    Ms = getPeakGain(S);  wB = bandwidth(T);
    fprintf('Kc = %.2f:  Ms = %.2f,  wB = %.2f\n', Kc, Ms, wB)
end
bodemag(feedback(1, L), feedback(L, 1)), legend('S', 'T')
