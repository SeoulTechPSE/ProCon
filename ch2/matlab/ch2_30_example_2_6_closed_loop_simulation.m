%% Ch.2 — Example 2.6 Closed-loop simulation
% Process Dynamics and Control, SeoulTech — slide 31
% https://seoultechpse.github.io/ProCon/ch2/ch2_analysis.html#/4/8
% Requires: Control System Toolbox

clear; close all; clc

Gp = tf(0.8, [5 1]);

Gc  = 10;                        % P
Gcl = feedback(Gp*Gc, 1);
step(Gcl); hold on

Gc  = tf([10 10], [1 0]);        % PI: 10(1 + 1/s)
Gcl = feedback(Gp*Gc, 1);
step(Gcl)
