%% Ch.6 — Smith predictor in code
% Process Dynamics and Control, SeoulTech — slide 26
% https://seoultechpse.github.io/ProCon/ch6/ch6_multiloop.html#/25
% Requires: Control System Toolbox

clear; close all; clc

s  = tf('s');
G0 = 0.8/(5*s + 1);                  % model without delay
Gd = ss(G0*exp(-2*s));               % plant with delay (ss: internal delays)
Gc = 5*(1 + 1/(5*s));                % PI, Kc = 5, tauI = 5

C_smith = feedback(Gc, G0 - Gd);     % controller + dead-time compensator
T_smith = feedback(C_smith*Gd, 1);   % = Gc*G0/(1+Gc*G0) * exp(-2s)
T_plain = feedback(Gc*Gd, 1);        % unstable
step(T_smith, 40)
