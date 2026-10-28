%% Ch.5 — Example 5.13 in code
% Process Dynamics and Control, SeoulTech — slide 33
% https://seoultechpse.github.io/ProCon/ch5/ch5_frequency.html#/32
% Requires: Control System Toolbox

clear; close all; clc

% --- setup from the slide 'Margins in code' ---
G = tf([-6 3], conv([10 1],[5 1]));
[Ku,~,wc] = margin(G);   Pu = 2*pi/wc;
% ---

tI = Pu/1.2;
Gs = tf([tI 1],[tI 0])*G;                       % G* = everything except Kc

Kcu = margin(Gs);   Kc_GM = Kcu/2;              % 1.86 -> 0.93

w = logspace(-3, 1, 1e5);
[m, p] = bode(Gs, w);   m = squeeze(m);   p = squeeze(p);
[~, i] = min(abs(p + 135));                     % phase = -135 deg
Kc_PM = 1/m(i)                                  % 0.60

Kc = min(Kc_GM, Kc_PM);
margin(Kc*Gs), stepinfo(feedback(Kc*Gs, 1))
