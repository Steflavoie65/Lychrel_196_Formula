# check_jacobian_mod2.py
# Build Jacobian matrix (entries over Z) for palindromicity constraints in carry variables
# and check rank/det modulo 2. Usage: run without args to test 196 and to scan hensel_lift_results.json

import json
from math import floor
from itertools import product

import sys

def digits(n):
    return list(map(int, str(n)))

# Build constraint equations F(c) = 0 (over Z) for palindromicity
# We'll use carries c_0..c_d (c_d is overflow). Indexing: j is LSB index 0..d-1
# b_j = a[d-1-j] + a[j] + c_{j-1} - 10*c_j
# For palindrome we require b_j - b_{d-1-j} = 0 for j=0..floor(d/2)-1
# Each constraint is linear in c variables: coefficients in Z

def build_jacobian(a):
    d = len(a)
    m = d//2
    # variables: c_0..c_d (d+1 variables)
    var_count = d+1
    rows = []
    for j in range(m):
        # constraint for pair j and d-1-j
        # b_j = a[d-1-j] + a[j] + c_{j-1} - 10*c_j
        # b_k where k = d-1-j: b_k = a[d-1-k] + a[k] + c_{k-1} - 10*c_k
        k = d-1-j
        # coefficients for variables c_0..c_d
        coeff = [0]*(var_count)
        # derivative of b_j wrt c_{j-1} is 1 (if j-1>=0)
        if j-1 >= 0:
            coeff[j-1] += 1
        # derivative wrt c_j is -10
        coeff[j] += -10
        # for b_k
        if k-1 >= 0:
            coeff[k-1] += -1  # subtracting b_k
        coeff[k] += 10  # subtracting b_k
        rows.append(coeff)
    return rows

# Compute rank mod 2 using Gaussian elimination over GF(2)

def rank_mod2(matrix):
    # matrix: list of rows, entries ints
    if not matrix:
        return 0
    rows = [list(map(lambda x: x & 1, row)) for row in matrix]
    nrows = len(rows)
    ncols = len(rows[0])
    rank = 0
    r = 0
    for c in range(ncols):
        # find pivot
        pivot = None
        for i in range(r, nrows):
            if rows[i][c] == 1:
                pivot = i
                break
        if pivot is None:
            continue
        # swap
        rows[r], rows[pivot] = rows[pivot], rows[r]
        # eliminate below
        for i in range(nrows):
            if i != r and rows[i][c] == 1:
                # rows[i] ^= rows[r]
                for j in range(c, ncols):
                    rows[i][j] ^= rows[r][j]
        r += 1
        rank += 1
        if r == nrows:
            break
    return rank


def analyze_n(n):
    a = digits(n)
    d = len(a)
    rows = build_jacobian(a)
    m = len(rows)
    var_count = d+1
    r = rank_mod2(rows)
    return dict(n=n, d=d, n_constraints=m, n_vars=var_count, rank_mod2=r, full_row_rank=(r==m))

if __name__ == '__main__':
    results = []
    # test 196
    results.append(analyze_n(196))
    # if hensel_lift_results.json exists, load keys (they seem to be strings of patterns)
    try:
        with open('../verifier/hensel_lift_results.json', 'r') as f:
            data = json.load(f)
        # keys look like pattern strings; attempt to interpret keys as decimal strings of candidate palindromes if possible
        # We'll only analyze up to 50 keys for speed
        cnt = 0
        for k in data.keys():
            if cnt >= 50:
                break
            # try to parse as int and analyze
            try:
                n = int(k)
            except Exception:
                # skip non-integers
                cnt += 1
                continue
            results.append(analyze_n(n))
            cnt += 1
    except FileNotFoundError:
        pass

    print(json.dumps(results, indent=2))
