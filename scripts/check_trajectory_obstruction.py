#!/usr/bin/env python3
"""Check trajectory obstruction for 196: for each T^j(196) compute

- obstruction modulo 2 (no palindromic carry assignment mod 2)
- Jacobian full-row-rank modulo 2
- if both hold -> tag as 'theoretical' by Hensel
- otherwise run empirical tests modulo 2^k up to k_max and tag accordingly

Writes results to ``results/trajectory_obstruction_log.json``.

Usage: python scripts/check_trajectory_obstruction.py --iterations 1001 --kmax 10
"""
import json
import argparse
import os
from itertools import product


def number_to_digits_int(n: int):
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        n, r = divmod(n, 10)
        digits.append(r)
    return digits  # LSB-first


def digits_to_number_int(digits):
    val = 0
    for d in reversed(digits):
        val = val * 10 + d
    return val


def apply_T_simple(n: int):
    digits = number_to_digits_int(n)
    d = len(digits)
    res_digits = [0] * (d + 1)
    carries = [0] * (d + 1)
    for i in range(d):
        j = d - 1 - i
        s = digits[i] + digits[j] + carries[i]
        res_digits[i] = s % 10
        carries[i + 1] = s // 10
    L = d
    if carries[d] > 0:
        res_digits[d] = carries[d]
        L = d + 1
    else:
        res_digits = res_digits[:d]
    Tn = digits_to_number_int(res_digits[:L])
    return Tn, res_digits[:L], carries


def is_palindrome_digits(digits):
    return digits == digits[::-1]


def check_palindrome_obstruction_mod2_fast(n: int):
    # returns True if obstruction (i.e., not a palindrome) modulo 2 at digit level
    digits = number_to_digits_int(n)
    d = len(digits)
    carries = [0] * (d + 1)
    result_digits = [0] * (d + 1)
    for i in range(d):
        j = d - 1 - i
        s = digits[i] + digits[j] + carries[i]
        result_digits[i] = s % 10
        carries[i + 1] = s // 10
    L = d
    if carries[d] > 0:
        result_digits[d] = carries[d]
        L = d + 1
    # check palindromicity of result digits
    is_pal = True
    for i in range(L // 2):
        if result_digits[i] != result_digits[L - 1 - i]:
            is_pal = False
            break
    return (not is_pal), result_digits[:L], carries


def build_jacobian(a_digits_msb):
    # a_digits_msb : list MSB->LSB, but our inner logic uses MSB->LSB; adapt
    a = list(a_digits_msb)
    d = len(a)
    m = d // 2
    var_count = d + 1
    rows = []
    for j in range(m):
        k = d - 1 - j
        coeff = [0] * var_count
        if j - 1 >= 0:
            coeff[j - 1] += 1
        coeff[j] += -10
        if k - 1 >= 0:
            coeff[k - 1] += -1
        coeff[k] += 10
        rows.append(coeff)
    return rows


def rank_mod2(matrix):
    # Fast rank over GF(2) using bit-packed rows for speed.
    # Each row becomes an integer where bit j corresponds to column j.
    if not matrix:
        return 0
    nrows = len(matrix)
    ncols = len(matrix[0])
    rows_int = []
    for row in matrix:
        v = 0
        for j, x in enumerate(row):
            if x & 1:
                v |= (1 << j)
        rows_int.append(v)

    rank = 0
    r = 0
    for c in range(ncols):
        pivot = None
        mask = 1 << c
        for i in range(r, nrows):
            if rows_int[i] & mask:
                pivot = i
                break
        if pivot is None:
            continue
        # swap pivot into row r
        rows_int[r], rows_int[pivot] = rows_int[pivot], rows_int[r]
        # eliminate bit c from all other rows
        for i in range(nrows):
            if i != r and (rows_int[i] & mask):
                rows_int[i] ^= rows_int[r]
        r += 1
        rank += 1
        if r == nrows:
            break
    return rank


def check_hensel_mod_pk(n: int, p: int, k: int):
    # quick necessary check: compute n+rev(n) digitwise and compare edge digits mod p^k
    digits = number_to_digits_int(n)
    d = len(digits)
    carries = [0] * (d + 1)
    result_digits = [0] * (d + 1)
    for i in range(d):
        j = d - 1 - i
        s = digits[i] + digits[j] + carries[i]
        result_digits[i] = s % 10
        carries[i + 1] = s // 10
    L = d
    if carries[d] > 0:
        result_digits[d] = carries[d]
        L = d + 1
    modulus = p ** k
    first_digit = result_digits[L - 1]
    last_digit = result_digits[0]
    return (first_digit % modulus) != (last_digit % modulus)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--iterations', type=int, default=1001)
    parser.add_argument('--start', type=int, default=196)
    parser.add_argument('--checkpoint', type=int, default=0,
                        help='write incremental checkpoint files every CHECKPOINT iterations (0 = disabled)')
    parser.add_argument('--kmax', type=int, default=10)
    parser.add_argument('--out', type=str, default=os.path.join('results', 'trajectory_obstruction_log.json'))
    args = parser.parse_args()

    N = args.iterations
    n = args.start
    kmax = args.kmax
    results = []

    for j in range(N):
        entry = {'iteration': j, 'n': n}
        obstruction_mod2, result_digits, carries = check_palindrome_obstruction_mod2_fast(n)
        entry['obstruction_mod2'] = bool(obstruction_mod2)
        # build jacobian from MSB->LSB digits
        a_msb = list(map(int, str(n)))
        rows = build_jacobian(a_msb)
        r = rank_mod2(rows)
        entry['jacobian_constraints'] = len(rows)
        entry['jacobian_vars'] = len(a_msb) + 1
        entry['jacobian_rank_mod2'] = int(r)
        entry['jacobian_full_row_rank'] = (r == len(rows))

        if not obstruction_mod2:
            entry['hensel_conclusion'] = 'no_mod2_obstruction'
        else:
            if entry['jacobian_full_row_rank'] and len(rows) > 0:
                entry['hensel_conclusion'] = 'theoretical_by_hensel'
            else:
                # run empirical tests up to kmax
                empirical_up_to = 0
                for k in range(1, kmax + 1):
                    ok = check_hensel_mod_pk(n, 2, k)
                    if ok:
                        empirical_up_to = k
                    else:
                        # found potential equality mod 2^k -> cannot claim obstruction at this level
                        break
                if empirical_up_to > 0:
                    entry['hensel_conclusion'] = f'empirical_obstruction_up_to_2^{empirical_up_to}'
                else:
                    entry['hensel_conclusion'] = 'needs_further_check'

        results.append(entry)

        # if the result is actually a palindrome (rare), stop and record
        if not entry['obstruction_mod2']:
            # double-check full palindromicity of T(n)
            if is_palindrome_digits(result_digits):
                entry['found_palindrome'] = True
                print(f'Palindrome found at iteration {j}: n={n}')
                break
        # advance
        n, _, _ = apply_T_simple(n)
        # periodic checkpoint dump
        checkpoint = args.checkpoint
        if checkpoint and ((j + 1) % checkpoint == 0 or j == N - 1):
            outpath = args.out
            chk_path = outpath + f'.part_{j+1}.json'
            tmp_path = chk_path + '.tmp'
            os.makedirs(os.path.dirname(outpath), exist_ok=True)
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump({'config': vars(args), 'results': results}, f, indent=2)
            os.replace(tmp_path, chk_path)
            print(f'Wrote checkpoint {chk_path} ({len(results)} entries)')

    # final write
    outpath = args.out
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    tmp_path = outpath + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump({'config': vars(args), 'results': results}, f, indent=2)
    os.replace(tmp_path, outpath)

    print(f'Wrote {len(results)} entries to {outpath}')


if __name__ == '__main__':
    main()
