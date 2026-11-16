%% Ch.2 — Digital PID in code
% Process Dynamics and Control, SeoulTech — slide 24
% https://seoultechpse.github.io/ProCon/ch2/ch2_analysis.html#/3/10
% Requires: Control System Toolbox

clear; close all; clc

Kc = 10; tI = 1; dt = 0.5;             % PI of Ex 2.6, sampling time 0.5
a = exp(-dt/5);                        % plant 0.8/(5s+1), exact over one hold interval
y = 0; p = 0; e1 = 0;
for k = 1:20
    e = 1 - y;                         % set point 1
    p = p + Kc*((e - e1) + dt/tI*e);   % velocity-form PI
    p = min(max(p, -20), 20);          % output limits: anti-windup for free
    e1 = e;
    y = a*y + 0.8*(1 - a)*p;           % process over one sample (zero-order hold)
    fprintf('%5.1f %7.3f %7.3f\n', k*dt, y, p)
end
% same plant model: Gd = c2d(tf(0.8, [5 1]), dt)   (zero-order hold)
