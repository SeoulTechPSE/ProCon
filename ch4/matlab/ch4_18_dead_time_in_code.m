%% Ch.4 — Dead time in code
% Process Dynamics and Control, SeoulTech — slide 19
% https://seoultechpse.github.io/ProCon/ch4/ch4_stability.html#/4/4
% Requires: Control System Toolbox

clear; close all; clc

wu  = fzero(@(w) 2*w + atan(5*w) - pi, [0.1 2]);
Kcu = sqrt(1 + 25*wu^2)/0.8                % 5.73

G = tf(0.8, [5 1]);
[n1,d1] = pade(2,1);   [Gm1,~,Wcg1] = margin(G*tf(n1,d1))     % 7.50, 1.18
Gd = tf(0.8, [5 1], 'InputDelay', 2);
[Gm, ~, Wcg] = margin(Gd)                                     % exact: 5.73, 0.895
