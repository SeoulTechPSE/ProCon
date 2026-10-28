%% Ch.6 — Example 6.1 in code
% Process Dynamics and Control, SeoulTech — slide 12
% https://seoultechpse.github.io/ProCon/ch6/ch6_multiloop.html#/2/9
% Requires: Control System Toolbox

clear; close all; clc

Gp = tf(0.8,[2 1]);  Gv = tf(0.5,[1 1]);  GL = tf(0.75,[1 1]);
Kc2 = 18;
Gv_s = feedback(Kc2*Gv, 1);                % G_v*
GL_s = minreal(GL/(1 + Kc2*Gv));           % G_L*

Kc = 3;  tI = 0.5;  Gc = Kc*tf([tI 1],[tI 0]);
load_single  = minreal(GL*Gp/(1 + Gc*Gv*Gp));
load_cascade = minreal(GL_s*Gp/(1 + Gc*Gv_s*Gp));
step(load_single, load_cascade, 30), legend('single loop','cascade')
