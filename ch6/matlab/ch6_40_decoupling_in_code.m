%% Ch.6 — Decoupling in code
% Process Dynamics and Control, SeoulTech — slide 41
% https://seoultechpse.github.io/ProCon/ch6/ch6_multiloop.html#/40
% Requires: Control System Toolbox

clear; close all; clc

s = tf('s');
G = [0.07*exp(-3*s)/(12*s+1), -0.05*exp(-s)/(15*s+1);
     0.10*exp(-4*s)/(11*s+1), -0.15*exp(-2*s)/(10*s+1)];
C = blkdiag(29.8*(1 + 1/(12.1*s)), -17.1*(1 + 1/(10.0*s)));

D_static  = [1, 0.714; 0.667, 1];                          % M = D * u
D_dynamic = [1, 0.714*(12*s+1)/(15*s+1);
             0.667*(10*s+1)/(11*s+1)*exp(-2*s), 1];
for D = {eye(2), D_static, D_dynamic}
    T = feedback(ss(G)*D{1}*C, eye(2));               % ss: mixed delays
    step(T(:,1), 80), hold on                              % step in r1 (x_D)
end
