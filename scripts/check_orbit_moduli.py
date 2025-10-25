#!/usr/bin/env python3
"""Analyse d'orbite modulo plusieurs modules M.

Pour chaque M fourni, génère T^j(196) pour j=0..max_iter-1, collecte l'ensemble
des résidus modulo M visités, et pour chaque état testé vérifie:
 - obstruction modulo 2 (exhaustive check rapide)
 - rang du jacobien modulo 2 (full row rank)

Écrit un résumé dans stdout et un JSON détaillé dans `results/orbit_moduli_summary.json`.
"""
import json
import os
from collections import defaultdict

# Try to import numba for accelerating Phase A (modular orbit detection).
try:
    from numba import njit
    NUMBA_AVAILABLE = True
except Exception:
    NUMBA_AVAILABLE = False
    def njit(func=None, **kwargs):
        # fallback decorator (no-op)
        if func is None:
            def wrap(f):
                return f
            return wrap
        return func


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


def check_palindrome_obstruction_mod2_fast(n: int):
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
    is_pal = True
    for i in range(L // 2):
        if result_digits[i] != result_digits[L - 1 - i]:
            is_pal = False
            break
    return (not is_pal), result_digits[:L], carries


def build_jacobian(a_digits_msb):
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
        mask = 1 << c
        pivot = None
        for i in range(r, nrows):
            if rows_int[i] & mask:
                pivot = i
                break
        if pivot is None:
            continue
        rows_int[r], rows_int[pivot] = rows_int[pivot], rows_int[r]
        for i in range(nrows):
            if i != r and (rows_int[i] & mask):
                rows_int[i] ^= rows_int[r]
        r += 1
        rank += 1
        if r == nrows:
            break
    return rank


def analyse_moduli(moduli, max_iter=20000):
    summary = {}
    for M in moduli:
        print(f'Phase A: computing orbit modulo M={M} (up to {max_iter} iterations)')
        orbit_size, cycle_start, seen_order = orbit_modulo_phase_a(M, max_iter)
        info = {'orbit_size_mod_M': orbit_size, 'cycle_start_index': cycle_start}
        # Heuristic: if orbit_size is small (<= 5000 or <= max_iter/4), run heavy checks on representatives
        if orbit_size <= 5000 or orbit_size <= max_iter // 4:
            print(f' orbit size {orbit_size} small -> running Phase B checks on encountered representatives')
            # run heavy checks but only on first occurrence of each residue's representative
            seen_representatives = {}
            n = 196
            state_info = {}
            for j in range(max_iter):
                r = n % M
                if r not in seen_representatives:
                    seen_representatives[r] = n
                if len(seen_representatives) >= orbit_size:
                    break
                n, _, _ = apply_T_simple(n)
            # now check each representative
            for r, rep in seen_representatives.items():
                obstruction_mod2, res_digits, carries = check_palindrome_obstruction_mod2_fast(rep)
                a_msb = list(map(int, str(rep)))
                rows = build_jacobian(a_msb)
                rnk = rank_mod2(rows)
                full = (rnk == len(rows))
                state_info[rep] = {
                    'mod_residue': r,
                    'obstruction_mod2': bool(obstruction_mod2),
                    'jacobian_constraints': len(rows),
                    'jacobian_rank_mod2': int(rnk),
                    'jacobian_full_row_rank': bool(full)
                }
            total_states = len(state_info)
            theoretical = sum(1 for v in state_info.values() if v['obstruction_mod2'] and v['jacobian_full_row_rank'] and v['jacobian_constraints']>0)
            needs_check = [rep for rep, v in state_info.items() if not (v['obstruction_mod2'] and v['jacobian_full_row_rank'] and v['jacobian_constraints']>0)]
            info.update({
                'checked_representatives': total_states,
                'theoretical_by_hensel_count': theoretical,
                'needs_further_check_count': len(needs_check),
                'example_needs_further_check': needs_check[:5]
            })
        else:
            print(f' orbit size {orbit_size} large -> skipping heavy Phase B checks for M={M} (to save time)')
        summary[M] = info
        print(f'M={M} summary: {info}')
    return summary


@njit
def orbit_modulo_phase_a_numba(M, max_iter):
    seen = set()
    n = 196
    for j in range(max_iter):
        r = n % M
        if r in seen:
            # approximate: return current size and j as cycle start indicator
            return len(seen), j, 0
        seen.add(r)
        # compute T(n) naively: but numba can't handle arbitrary big ints well; keep in Python fallback
        n = n + 0  # placeholder
    return len(seen), -1, 0


def orbit_modulo_phase_a_python(M, max_iter=20000):
    seen = {}
    n = 196
    for j in range(max_iter):
        r = n % M
        if r in seen:
            return len(seen), seen[r], list(seen.keys())
        seen[r] = j
        n, _, _ = apply_T_simple(n)
    return len(seen), -1, list(seen.keys())


def orbit_modulo_phase_a(M, max_iter=20000):
    # Choose implementation
    if NUMBA_AVAILABLE:
        # Numba path: but fallback because T(n) with big ints not supported; use python instead
        try:
            return orbit_modulo_phase_a_python(M, max_iter)
        except Exception:
            return orbit_modulo_phase_a_python(M, max_iter)
    else:
        return orbit_modulo_phase_a_python(M, max_iter)


def main():
    moduli = [2**10, 2**12, 10**6]
    summary = analyse_moduli(moduli, max_iter=20000)
    out = os.path.join('results', 'orbit_moduli_summary.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print('Wrote summary to', out)


if __name__ == '__main__':
    main()
