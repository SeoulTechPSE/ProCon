%% Ch.4 — Routh array in code
% Process Dynamics and Control, SeoulTech — slide 14
% https://seoultechpse.github.io/ProCon/ch4/ch4_stability.html#/13
% Requires: Control System Toolbox, Symbolic Math Toolbox

clear; close all; clc

syms s Kc tI positive
p = sym2poly_sym(expand((s+3)*(s+2)*(s+1) + Kc), s);   % [1 6 11 Kc+6]
R = routh_array(p);   R(:,1)                         % first column

function c = sym2poly_sym(P, s), c = coeffs(P, s, 'All'); end

function R = routh_array(p)            % basic version (no special cases)
  n = numel(p)-1;  cols = floor(n/2)+1;  R = sym(zeros(n+1, cols));
  R(1,1:numel(p(1:2:end))) = p(1:2:end);
  R(2,1:numel(p(2:2:end))) = p(2:2:end);
  for i = 3:n+1
    for j = 1:cols-1
      R(i,j) = simplify((R(i-1,1)*R(i-2,j+1) - R(i-2,1)*R(i-1,j+1))/R(i-1,1));
    end
  end
end
