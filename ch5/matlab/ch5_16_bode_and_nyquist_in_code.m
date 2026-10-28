%% Ch.5 — Bode and Nyquist in code
% Process Dynamics and Control, SeoulTech — slide 17
% https://seoultechpse.github.io/ProCon/ch5/ch5_frequency.html#/3/10
% Requires: Control System Toolbox

clear; close all; clc

G = tf(1, [2 1]);                       % Ex 5.2
figure(1), bode(G)
figure(2), nyquist(G)

G6 = tf(1, [10 1], 'InputDelay', 2);    % Ex 5.6: exact dead time
figure(3), bode(G6)
figure(4), nyquist(G6)

K = 1; tau = 2;                         % Ex 5.3: family in zeta
for zeta = [1.2 1.0 0.8 0.6 0.4 0.2]
    bode(tf(K, [tau^2 2*zeta*tau 1])), hold on
end
