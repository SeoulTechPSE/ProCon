%% Ch.5 — Margins in code
% Process Dynamics and Control, SeoulTech — slide 29
% https://seoultechpse.github.io/ProCon/ch5/ch5_frequency.html#/4/11
% Requires: Control System Toolbox

clear; close all; clc

G = tf([-6 3], conv([10 1],[5 1]));
[Ku,~,wc] = margin(G);   Pu = 2*pi/wc;      % 2.5, 15.2 s

Kc = Ku/2.2;   tI = Pu/1.2;                 % Ziegler-Nichols PI
L = Kc*tf([tI 1],[tI 0])*G;
[GM,PM,wc,wg] = margin(L)                   % 1.63, 19.4 deg
theta_max = PM*pi/180/wg                    % 1.43 s
margin(L)                                   % Bode plot with margins marked
