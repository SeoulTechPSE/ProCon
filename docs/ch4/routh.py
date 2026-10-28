"""Routh array with sympy — handles symbolic gains and both special cases.

    from routh import routh_array
    s, Kc = sp.symbols('s K_c')
    R = routh_array((s+1)*(s+2)*(s+3) + Kc, s)
"""
import sympy as sp

eps = sp.Symbol('epsilon', positive=True)


def routh_array(poly, s, verbose=True):
    a = sp.Poly(sp.expand(poly), s).all_coeffs()          # [a_n, ..., a_0]
    n = len(a) - 1
    cols = n // 2 + 1
    pad = lambda r: list(r) + [0] * (cols - len(r))
    R = [pad(a[0::2]), pad(a[1::2])]
    for i in range(2, n + 1):
        up, lo = R[-2], R[-1]
        if all(sp.simplify(x) == 0 for x in lo):              # special case 2: row of zeros
            order = n - i + 2                                  # order of auxiliary polynomial
            A = sum(up[k] * s**(order - 2 * k) for k in range(cols) if order - 2 * k >= 0)
            dA = sp.Poly(sp.diff(A, s), s).all_coeffs()
            R[-1] = lo = pad(dA)
            if verbose:
                print(f"row s^{order-1} is zero -> auxiliary polynomial A(s) = {sp.factor(A)}")
        if sp.simplify(lo[0]) == 0:                            # special case 1: zero in first column
            lo = [eps] + lo[1:]; R[-1] = lo
            if verbose:
                print(f"first-column zero in row s^{n-i+1} -> replaced by epsilon")
        new = [sp.simplify((lo[0] * up[k + 1] - up[0] * lo[k + 1]) / lo[0]) for k in range(cols - 1)] + [0]
        R.append(new)
    if verbose:
        for i, r in enumerate(R):
            print(f"s^{n-i}:", "  ".join(str(x) for x in r))
    return R


def first_column(R):
    return [r[0] for r in R]


if __name__ == "__main__":
    s, Kc = sp.symbols('s K_c')
    print("--- Ex 4.2");   routh_array((s+1)*(s+2)*(s+3) + Kc, s)
    print("--- Ex 4.2 at Kc=60 (row of zeros)");  routh_array((s+1)*(s+2)*(s+3) + 60, s)
    print("--- epsilon case"); R = routh_array(s**4 + s**3 + 2*s**2 + 2*s + 3, s)
    print([sp.limit(c, eps, 0, '+') for c in first_column(R)])
