%% Ch.6 — MPC in code
% Process Dynamics and Control, SeoulTech — slide 47
% https://seoultechpse.github.io/ProCon/ch6/ch6_multiloop.html#/9/5
% Requires: Control System Toolbox

clear; close all; clc

% Model Predictive Control Toolbox
G = tf(0.8, [5 1], 'InputDelay', 2);
mpcobj = mpc(c2d(G, 0.5), 0.5, 30, 6);        % Ts, prediction P, control M
mpcobj.MV.Min = 0;  mpcobj.MV.Max = 1.6;
mpcobj.Weights.MVRate = 0.05;
T = 120;  r = ones(T, 1);
[y, t, u] = sim(mpcobj, T, r);
subplot(2,1,1), plot(t, y), subplot(2,1,2), stairs(t, u)
