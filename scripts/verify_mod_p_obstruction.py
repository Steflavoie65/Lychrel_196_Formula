#!/usr/bin/env python3
"""Generic verifier for modulo-p obstruction for the Lychrel 196 trajectory.

Builds linear systems modulo p encoding digit formation and palindromic constraints
and checks solvability over Z/pZ for each iterate. Outputs JSON certificate.
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
    return digs


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
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    M = [row[:] for row in A]
    B = b[:]
    row = 0
    col = 0
    inv = lambda a: pow(a, -1, p)
    while row < m and col < n:
        sel = None
        for i in range(row, m):
            if M[i][col] % p != 0:
                sel = i
                break
        if sel is None:
            col += 1
            continue
        M[row], M[sel] = M[sel], M[row]
        B[row], B[sel] = B[sel], B[row]
        factor = M[row][col] % p
        invf = inv(factor)
        for j in range(col, n):
            M[row][j] = (M[row][j] * invf) % p
        B[row] = (B[row] * invf) % p
        for i in range(m):
            if i != row and M[i][col] % p != 0:
                factor = M[i][col] % p
                for j in range(col, n):
                    M[i][j] = (M[i][j] - factor * M[row][j]) % p
                B[i] = (B[i] - factor * B[row]) % p
        row += 1
        col += 1
    for i in range(row, m):
        if not any((M[i][j] % p) != 0 for j in range(n)):
            if B[i] % p != 0:
                return False, None
    x = [0] * n
    piv_cols = []
    for i in range(min(m, n)):
        for j in range(n):
            if M[i][j] % p == 1:
                piv_cols.append((i, j))
                break
    for i, j in piv_cols:
        x[j] = B[i] % p
    return True, x


def build_linear_system_mod_p(a_digits, p):
    d = len(a_digits)
    systems = []
    for L in (d, d + 1):
        var_count = (d + 1) + L
        A = []
        B = []
        for i in range(d):
            row = [0] * var_count
            if i - 1 >= 0:
                row[i - 1] = 1
            row[(d + 1) + i] = (-1) % p
            rhs = (a_digits[i] + a_digits[d - 1 - i]) % p
            A.append([x % p for x in row])
            B.append(rhs)
        if L == d + 1:
            row = [0] * var_count
            row[d] = (-1) % p
            row[(d + 1) + d] = 1
            A.append([x % p for x in row])
            B.append(0)
        for i in range(L // 2):
            row = [0] * var_count
            row[(d + 1) + i] = 1
            row[(d + 1) + (L - 1 - i)] = (-1) % p
            A.append([x % p for x in row])
            B.append(0)
        systems.append((A, B, var_count, L))
    return systems


def check_mod_p_obstruction_for_n(n: int, p: int):
    a = number_to_digits_lsb(n)
    systems = build_linear_system_mod_p(a, p)
    for A, B, var_count, L in systems:
        solvable, sol = gauss_jordan_mod_p(A, B, p)
        if solvable:
            return False, {'L': L}
    return True, None


def run_verify(p: int, iterations: int, start: int = 196, outpath: str = None):
    results = []
    n = start
    for j in range(iterations):
        obstruct, info = check_mod_p_obstruction_for_n(n, p)
        results.append({'iteration': j, 'n': n, f'mod{p}_obstruction': bool(obstruct), 'info': info})
        n, _, _ = apply_T(n)
    data = {
        'timestamp': datetime.utcnow().isoformat(),
        'test': f'verify_mod{p}_obstruction',
        'p': p,
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--prime', type=int, required=True)
    parser.add_argument('--iterations', type=int, default=1000)
    parser.add_argument('--start', type=int, default=196)
    parser.add_argument('--out', type=str, default=None)
    args = parser.parse_args()
    p = args.prime
    out = args.out or f'results/verify_mod{p}_{args.iterations}.json'
    print(f'Running verify_mod{p} for {args.iterations} iterations')
    run_verify(p, args.iterations, args.start, out)
    print('Wrote', out)


if __name__ == '__main__':
    main()
