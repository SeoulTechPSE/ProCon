%% Ch.1 — Example 1.10 Padé approximation of $e^{-3s}/(10s+1)$
% Process Dynamics and Control, SeoulTech — slide 41
% https://seoultechpse.github.io/ProCon/ch1/ch1_dynamics.html#/40
% Requires: Control System Toolbox

clear; close all; clc

G  = tf(1, [10 1]);
P1 = tf([-1.5 1], [1.5 1]);   % pade(3,1)
step(G*P1); hold on
step(G*exp(-3*tf('s')))      % exact delay
legend('Pade 1/1', 'exact')
