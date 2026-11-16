%% Ch.1 — Example 1.3 in code
% Process Dynamics and Control, SeoulTech — slide 10
% https://seoultechpse.github.io/ProCon/ch1/ch1_dynamics.html#/2/7
% Requires: Control System Toolbox

clear; close all; clc

q = 100; V = 100; cAi = 1; Ti = 350; rhoCp = 239; dH = -5e4; ER = 8750; k0 = 7.2e10; UA = 5e4;
f = @(t, x, Tc) [q/V*(cAi - x(1)) - k0*exp(-ER/x(2))*x(1);
                 q/V*(Ti - x(2)) - dH/rhoCp*k0*exp(-ER/x(2))*x(1) + UA/(V*rhoCp)*(Tc - x(2))];
[~, x] = ode45(@(t, x) f(t, x, 290), [0 50], [0.95; 320]);
xs = x(end, :)';                                        % steady state 0.952, 312.7
k = k0*exp(-ER/xs(2));  kp = k*ER/xs(2)^2;
A = [-q/V - k, -kp*xs(1); -dH*k/rhoCp, -q/V - UA/(V*rhoCp) - dH*kp*xs(1)/rhoCp];
B = [0; UA/(V*rhoCp)];
lin = ss(A, B, [0 1], 0);                               % output T'
t = linspace(0, 10, 1001)';
for dTc = [2 10 -10 20]
    [~, x] = ode45(@(t, x) f(t, x, 290 + dTc), t, xs);
    plot(t, x(:,2) - xs(2), t, lsim(lin, dTc*ones(size(t)), t), '--'), hold on
end
xlabel('time (min)'), ylabel('T'' (K)')
