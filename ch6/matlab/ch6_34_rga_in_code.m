%% Ch.6 — RGA in code
% Process Dynamics and Control, SeoulTech — slide 35
% https://seoultechpse.github.io/ProCon/ch6/ch6_multiloop.html#/7/8
% Requires: Control System Toolbox

clear; close all; clc

rga = @(K) K .* inv(K).';                    % Lambda = K o (K^-1)^T

m1 = 0.1;  m2 = 10;  F = m1 + m2;
K = [m2/F^2, -m1/F^2;
     1,       1     ];
rga(K)                                       % [0.9901 0.0099; 0.0099 0.9901]

K66 = [0.07 -0.05; 0.1 -0.15];               % distillation, Ex 6.6
rga(K66)                                     % [1.91 -0.91; -0.91 1.91]
