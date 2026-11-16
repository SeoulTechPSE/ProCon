%% Ch.1 — State-space form
% Process Dynamics and Control, SeoulTech — slide 11
% https://seoultechpse.github.io/ProCon/ch1/ch1_dynamics.html#/2/8
% Requires: Control System Toolbox

clear; close all; clc

% --- setup from the slide 'Example 1.3 in code' ---
q = 100; V = 100; cAi = 1; Ti = 350; rhoCp = 239; dH = -5e4; ER = 8750; k0 = 7.2e10; UA = 5e4;
f = @(t, x, Tc) [q/V*(cAi - x(1)) - k0*exp(-ER/x(2))*x(1);
                 q/V*(Ti - x(2)) - dH/rhoCp*k0*exp(-ER/x(2))*x(1) + UA/(V*rhoCp)*(Tc - x(2))];
[~, x] = ode45(@(t, x) f(t, x, 290), [0 50], [0.95; 320]);  xs = x(end, :)';
k = k0*exp(-ER/xs(2));  kp = k*ER/xs(2)^2;
A = [-q/V - k, -kp*xs(1); -dH*k/rhoCp, -q/V - UA/(V*rhoCp) - dH*kp*xs(1)/rhoCp];
B = [0; UA/(V*rhoCp)];
% ---

sys = ss(A, B, eye(2), 0);               % outputs c_A', T'
eig(A)                                   % poles: -1.092, -2.151
tf(sys)                                  % T'/Tc' = (2.092 s + 2.198)/(s^2 + 3.243 s + 2.348)
