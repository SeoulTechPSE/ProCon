%% Ch.3 — Van de Vusse in code
% Process Dynamics and Control, SeoulTech — slide 13
% https://seoultechpse.github.io/ProCon/ch3/ch3_tuning.html#/12
% Requires: Control System Toolbox

clear; close all; clc

Gp = tf(0.5858*[-0.3549 1], [0.1858 0.8627 1]);
[Kcu, ~, wu] = margin(Gp);   Tu = 2*pi/wu;      % 4.150, 1.462

C_P   = 0.5*Kcu;
C_PI  = pidstd(0.455*Kcu, 0.833*Tu);
C_PID = pidstd(0.6*Kcu, 0.5*Tu, 0.125*Tu, 10);  % N = 10 <-> alpha = 0.1
step(feedback(C_P*Gp,1), feedback(C_PI*Gp,1), feedback(C_PID*Gp,1), 5)
legend('P','PI','PID')
