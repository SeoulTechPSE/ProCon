%% Ch.3 — Tuning rules in code
% Process Dynamics and Control, SeoulTech — slide 16
% https://seoultechpse.github.io/ProCon/ch3/ch3_tuning.html#/15
% Requires: Control System Toolbox

clear; close all; clc

G = tf(1, conv(conv([2 1],[1 1]),[0.5 1]));
[y, t] = step(G, 30);
t28 = t(find(y >= 0.283, 1));   t63 = t(find(y >= 0.632, 1));
tau = 1.5*(t63 - t28);   theta = t63 - tau;   K = y(end);   % 2.57, 1.14, 1

r = theta/tau;                                    % ITAE set point, PID
Kc = 0.965/K*(1/r)^0.855;  tI = tau/(0.796 - 0.147*r);  tD = 0.308*tau*r^0.929;
C = pidstd(Kc, tI, tD, 10);
figure, step(feedback(C*G, 1)),  figure, margin(C*G)
