%% Ch.1 — Partial fractions by computer
% Process Dynamics and Control, SeoulTech — slide 20
% https://seoultechpse.github.io/ProCon/ch1/ch1_dynamics.html#/19
% Requires: Control System Toolbox, Symbolic Math Toolbox

clear; close all; clc

[r, p, k] = residue([6 0 -12], [1 1 -4 -4])      % Ex 1.5: residues and poles
roots([1 1 -4 -4])                               % 2, -2, -1

syms s t
ilaplace((s + 5)/(s^2 + 4*s + 13))               % Ex 1.6
ilaplace(2/((s + 1)^3*(s + 2)))                  % Ex 1.7
partfrac(2/((s + 1)^3*(s + 2)), s)
