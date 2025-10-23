import json
from itertools import combinations
import sympy as sp
import time

REPS = [14456,24242,10301,10213,12121,12324,41204,23222,11117,34243,14342,20091,10302,15241,11422,32122,22121,13430,10310,42113,41414]
# Étendu à 120 pour une vérification Hensel plus profonde
K_MAX = 120


def digits_rev(n):
    return list(map(int, str(n)[::-1]))


def build_matrix(d):
    m = d//2
    A = sp.zeros(m, d)
    for i in range(m):
        j = d-1-i
        if i-1 >= 0:
            A[i, i-1] += 1
        A[i, i] += -10
        if j-1 >= 0:
            A[i, j-1] += -1
        A[i, j] += 10
    return A


def F_vector(rep, c):
    # returns vector length m of palindromicity equations evaluated at integer carries c
    s = str(rep)
    d = len(s)
    a = list(map(int, s[::-1]))
    b = [0]*d
    for i in range(d):
        c_prev = c[i-1] if i-1 >=0 else 0
        s_i = a[i] + a[d-1-i] + c_prev
        bi = s_i - 10*c[i]
        b[i] = bi
    # build m constraints: for i in 0..m-1, we want b[i] - b[d-1-i] == 0 (if no overflow)
    m = d//2
    vec = [0]*m
    for i in range(m):
        vec[i] = b[i] - b[d-1-i]
    return vec


def try_hensel_for_rep(rep, minor_cols, base_c):
    s = str(rep)
    d = len(s)
    m = d//2
    A = build_matrix(d)
    cols_sel = list(minor_cols)
    free_cols = [c for c in range(d) if c not in cols_sel]
    M = A[:, cols_sel]
    # work modulo increasing powers of 2
    c_curr = [int(x) for x in base_c]
    for k in range(1, K_MAX+1):
        modulus = 1 << k
        # compute residual r = F(c_curr) mod 2^k
        r = [int(x) % modulus for x in F_vector(rep, c_curr)]
        if all(x % modulus == 0 for x in r):
            # already satisfied modulo 2^k
            continue
        # we need to solve for delta on selected cols to cancel r modulo 2^k
        # build A_mod = A[:, cols_sel] mod 2^k
        A_mod = sp.Matrix([[int(A[i,j]) % modulus for j in cols_sel] for i in range(m)])
        try:
            Ainv = A_mod.inv_mod(modulus)
        except Exception:
            return False, k-1, c_curr
        # compute delta_sel = (-r) in Z_mod multiplied by Ainv
        rvec = sp.Matrix([(-x) % modulus for x in r])
        delta_sel = Ainv * rvec
        # convert delta_sel to integers 0..modulus-1
        delta_sel_ints = [int(x % modulus) for x in delta_sel]
        # apply delta to c_curr for selected cols
        for idx, col in enumerate(cols_sel):
            c_curr[col] = (c_curr[col] + delta_sel_ints[idx]) % modulus
        # check digit constraints (we need actual integer bi in 0..9)
        # compute b_i using current integer representatives (choose smallest nonnegative repr)
        s_digits = list(map(int, s[::-1]))
        ok = True
        for i in range(d):
            c_prev = c_curr[i-1] if i-1>=0 else 0
            s_i = s_digits[i] + s_digits[d-1-i] + c_prev
            bi = s_i - 10 * c_curr[i]
            # we interpret c_curr[i] as integer in 0..modulus-1; if bi not in 0..9 then fail
            if not (0 <= bi <= 9):
                ok = False
                break
        if not ok:
            return False, k, c_curr
        # otherwise continue to next k
    return True, K_MAX, c_curr


def main():
    with open('verifier/hensel_applicability_summary.json','r') as f:
        hens = json.load(f)
    with open('verifier/closure_mod2k_targeted_results.json','r') as f:
        modres = json.load(f)

    results = {}
    for rep in REPS:
        info = hens.get(str(rep))
        if not info:
            results[rep] = {'status':'no_hensel_info'}
            continue
        if not info['base_sol_exists_mod2'] or info['invertible_minors']==0:
            results[rep] = {'status':'no_base_or_no_minor', 'info':info}
            continue
        minor = info['some_minors'][0]['cols']
        base_c = info['base_sol_mod2']
        start = time.time()
        ok, reached_k, c_final = try_hensel_for_rep(rep, minor, base_c)
        elapsed = time.time() - start
        results[rep] = {'minor_used': minor, 'base_c': base_c, 'hensel_lift_success': ok, 'reached_k': reached_k, 'final_c_repr': c_final, 'time_s': elapsed}

    with open('verifier/hensel_lift_results.json','w') as f:
        json.dump(results, f, indent=2)
    print('Wrote verifier/hensel_lift_results.json')


if __name__ == '__main__':
    main()
