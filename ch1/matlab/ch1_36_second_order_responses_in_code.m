%% Ch.1 — Second-order responses in code
% Process Dynamics and Control, SeoulTech — slide 37
% https://seoultechpse.github.io/ProCon/ch1/ch1_dynamics.html#/7/5
% Requires: Control System Toolbox

clear; close all; clc

t = 0:0.01:15;
step(tf(1, [1 1 1]), tf(1, [1 2 1]), tf(1, [1 3 1]), t)   % zeta = 0.5, 1, 1.5
legend('\zeta = 0.5', '\zeta = 1', '\zeta = 1.5')

S = stepinfo(tf(1, [1 0.6 1]))                             % zeta = 0.3
% Simulink: Step -> three Transfer Fcn blocks in parallel -> Scope
