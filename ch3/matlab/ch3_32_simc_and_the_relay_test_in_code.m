%% Ch.3 — SIMC and the relay test in code
% Process Dynamics and Control, SeoulTech — slide 33
% https://seoultechpse.github.io/ProCon/ch3/ch3_tuning.html#/3/14
% Requires: Control System Toolbox

clear; close all; clc

% SIMC, FOPDT K e^{-theta s}/(tau s + 1), tau_c = theta
K = 1; tau = 20; theta = 1; tc = theta;
Kc = tau/(K*(tc + theta));   tI = min(tau, 4*(tc + theta))          % 10, 8
G = tf(1, [tau 1], 'InputDelay', theta);
C = pidstd(Kc, tI);
step(feedback(G, C))                                                % unit load at the process input

% relay test: Simulink Relay block (+-1) in place of the controller, or
Gp = tf(1, conv(conv([2 1], [1 1]), [0.5 1]));
[Kcu, ~, wu] = margin(Gp);  Tu = 2*pi/wu                            % exact values to compare
