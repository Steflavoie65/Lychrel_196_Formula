#!/usr/bin/env python3
"""Rigorous verifier for modulo-5 obstruction for the Lychrel 196 trajectory.

For each iterate T^j(196) this script builds the linear system of
congruences modulo 5 encoding digit formation and palindromic constraints
and checks solvability over Z/5Z. If no solution exists, we record an
obstruction modulo 5 for that iterate.

Outputs a JSON certificate in `results/`.
"""
from pathlib import Path
from datetime import datetime
import json
import argparse


def number_to_digits_lsb(n: int):
    if n == 0:
        return [0]
    digs = []
    while n > 0:
        n, r = divmod(n, 10)
        digs.append(r)
    return digs  # LSB-first


def digits_to_number(digs):
    v = 0
    for d in reversed(digs):
        v = v * 10 + d
    return v


def apply_T(n: int):
    digs = number_to_digits_lsb(n)
    d = len(digs)
    res = [0] * (d + 1)
    carries = [0] * (d + 1)
    for i in range(d):
        j = d - 1 - i
        s = digs[i] + digs[j] + carries[i]
        res[i] = s % 10
        carries[i + 1] = s // 10
    L = d
    if carries[d] > 0:
        res[d] = carries[d]
        L = d + 1
    return digits_to_number(res[:L]), res[:L], carries


def gauss_jordan_mod_p(A, b, p):
    # Solve A x = b mod p; return (is_solvable, one_solution_or_none)
    # A: list of rows (lists), b: list
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    # copy
    M = [row[:] for row in A]
    B = b[:]
    row = 0
    col = 0
    inv = lambda a: pow(a, -1, p)
    while row < m and col < n:
        # find pivot
        sel = None
        for i in range(row, m):
            if M[i][col] % p != 0:
                sel = i
                break
        if sel is None:
            col += 1
            continue
        # swap
        M[row], M[sel] = M[sel], M[row]
        B[row], B[sel] = B[sel], B[row]
        # normalize
        factor = M[row][col] % p
        invf = inv(factor)
        for j in range(col, n):
            M[row][j] = (M[row][j] * invf) % p
        B[row] = (B[row] * invf) % p
        # eliminate
        for i in range(m):
            if i != row and M[i][col] % p != 0:
                factor = M[i][col] % p
                for j in range(col, n):
                    M[i][j] = (M[i][j] - factor * M[row][j]) % p
                B[i] = (B[i] - factor * B[row]) % p
        row += 1
        col += 1

    # Check consistency: rows of zeros in M must have 0 in B
    for i in range(row, m):
        if any((M[i][j] % p) != 0 for j in range(n)):
            continue
        if B[i] % p != 0:
            return False, None

    # construct one solution by back substitution on reduced row-echelon form
    x = [0] * n
    # find pivot columns
    piv_cols = []
    for i in range(min(m, n)):
        for j in range(n):
            if M[i][j] % p == 1:
                piv_cols.append((i, j))
                break
    for i, j in piv_cols:
        x[j] = B[i] % p
    return True, x


def build_linear_system_mod5(a_digits):
    # Given the original digits a (LSB-first list)
    d = len(a_digits)
    systems = []
    for L in (d, d + 1):
        var_count = (d + 1) + L
        A = []
        B = []
        # digit formation equations
        for i in range(d):
            row = [0] * var_count
            if i - 1 >= 0:
                row[i - 1] = 1
            row[(d + 1) + i] = (-1) % 5
            rhs = (a_digits[i] + a_digits[d - 1 - i]) % 5
            A.append([x % 5 for x in row])
            B.append(rhs)

        if L == d + 1:
            row = [0] * var_count
            row[d] = (-1) % 5
            row[(d + 1) + d] = 1
            A.append([x % 5 for x in row])
            B.append(0)

        for i in range(L // 2):
            row = [0] * var_count
            row[(d + 1) + i] = 1
            row[(d + 1) + (L - 1 - i)] = (-1) % 5
            A.append([x % 5 for x in row])
            B.append(0)

        systems.append((A, B, var_count, L))

    return systems


def check_mod5_obstruction_for_n(n: int):
    a = number_to_digits_lsb(n)
    systems = build_linear_system_mod5(a)
    for A, B, var_count, L in systems:
        solvable, sol = gauss_jordan_mod_p(A, B, 5)
        if solvable:
            return False, {'L': L}
    return True, None


def run_verify(iterations: int, start: int = 196, outpath: str = None):
    results = []
    n = start
    for j in range(iterations):
        obstruct, info = check_mod5_obstruction_for_n(n)
        results.append({'iteration': j, 'n': n, 'mod5_obstruction': bool(obstruct), 'info': info})
        n, _, _ = apply_T(n)
    data = {
        'timestamp': datetime.utcnow().isoformat(),
        'test': 'verify_mod5_obstruction',
        'start': start,
        'iterations': iterations,
        'results': results
    }
    if outpath:
        Path(outpath).parent.mkdir(parents=True, exist_ok=True)
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--iterations', type=int, default=1000)
    p.add_argument('--start', type=int, default=196)
    p.add_argument('--out', type=str, default='results/verify_mod5.json')
    args = p.parse_args()
    print(f"Running verify_mod5 for {args.iterations} iterations starting at {args.start}")
    data = run_verify(args.iterations, args.start, args.out)
    print(f"Wrote {args.out}")


if __name__ == '__main__':
    main()
