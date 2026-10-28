%% Ch.4 — Example 4.7 in code
% Process Dynamics and Control, SeoulTech — slide 36
% https://seoultechpse.github.io/ProCon/ch4/ch4_stability.html#/6/3
% Requires: Control System Toolbox

clear; close all; clc

G = tf(1, conv([2 1],[4 1]));
rlocus(G); axis([-0.8 0 -1 1]); sgrid(0.7, 0.2:0.2:1)   % wn > 0
zeta = 0.7;
Kc = 9/(8*zeta^2) - 1                 % exact: 1.296  (rlocfind click: ~1.23)
pole(feedback(Kc*G,1))
stepinfo(feedback(Kc*G,1))
