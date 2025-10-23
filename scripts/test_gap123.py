#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_3gaps_fast.py
Version optimisée du TEST ULTIME (GAP1, GAP2, GAP3) pour Lychrel (ex: 196).
Auteur: Stéphane Lavoie + optimisation ChatGPT
Date: Octobre 2025

But: conçu pour reproduire exactement la logique de ton script original
mais en beaucoup plus rapide (algorithmes O(d) par itération).
"""

import argparse
import json
import time
from datetime import datetime
from math import floor
from typing import List, Tuple, Optional

# -------------------------
# UTILITAIRES ENTIER RAPIDES
# -------------------------
def number_to_digits_int(n: int) -> List[int]:
    """Retourne la liste des chiffres LSB-first (divmod loop)."""
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        n, r = divmod(n, 10)
        digits.append(r)
    return digits  # LSB first

def digits_to_number_int(digits: List[int]) -> int:
    """Convertion LSB-first -> int."""
    val = 0
    # reversed iterate: MSB -> LSB
    for d in reversed(digits):
        val = val * 10 + d
    return val

# -------------------------
# OPÉRATION T (n -> n + rev(n)) EFFICIENTE
# -------------------------
def apply_T_with_details_int(n: int):
    """
    Applique T(n) = n + rev(n) en entier, retourne:
      - T_n (int)
      - carries (list des retenues avant l'addition de chaque position, length = d+1)
      - details : dictionnaire avec asymétries n, T_n et deltas
    Opérations en O(d) sans conversion str fréquente.
    """
    digits = number_to_digits_int(n)
    d = len(digits)
    # prépare result buffer de longueur au plus d+1
    res_digits = [0] * (d + 1)
    carries = [0] * (d + 1)  # carries[i] retenue avant position i ; carries[0]=0
    carries[0] = 0

    # addition digit par digit
    for i in range(d):
        j = d - 1 - i
        s = digits[i] + digits[j] + carries[i]
        res_digits[i] = s % 10
        carries[i + 1] = s // 10

    # gérer overflow final
    L = d
    if carries[d] > 0:
        res_digits[d] = carries[d]
        L = d + 1
    else:
        # chop trailing unused slot
        res_digits = res_digits[:d]

    T_n = digits_to_number_int(res_digits[:L])

    # calcul des asymétries
    details = compute_asymmetries_from_digits(digits, res_digits[:L], carries)
    return T_n, carries, details

# -------------------------
# COMPUTE ASYMMETRIES (GAP1 & GAP3)
# -------------------------
def compute_asymmetries_from_digits(digits_n: List[int], digits_Tn: List[int], carries: List[int]):
    """
    Calcule A_ext, A_int, A_carry (selon ta définition),
    et les deltas attendus. Conserve la sémantique de ton script.
    """
    d_n = len(digits_n)
    d_Tn = len(digits_Tn)

    # A_ext : différence extrémités absolue
    A_ext_n = abs(digits_n[0] - digits_n[d_n - 1])

    # A_int : somme pondérée 2^(i-1) * |d_i - d_{m-1-i}| pour i>=1
    A_int_n = 0
    pow2 = 1
    for i in range(1, d_n // 2):
        # pondération = 2^(i-1)
        A_int_n += pow2 * abs(digits_n[i] - digits_n[d_n - 1 - i])
        pow2 <<= 1

    # pour T(n)
    A_ext_Tn = abs(digits_Tn[0] - digits_Tn[d_Tn - 1])
    A_int_Tn = 0
    pow2 = 1
    for i in range(1, d_Tn // 2):
        A_int_Tn += pow2 * abs(digits_Tn[i] - digits_Tn[d_Tn - 1 - i])
        pow2 <<= 1

    # A_carry calculation:
    # dans ton script original: A_carry_Tn += 0.5 * abs(ci - cj) pour chaque position
    # plus +1 si overflow. Pour éviter floats coûteux, on calcule A_carry_twice = 2 * A_carry
    A_carry_twice = 0
    # length for carries considered = len(carries) (normalement d+1)
    # mapping j = d_Tn - 1 - i (comme dans ton code)
    clen = len(carries)
    for i in range(clen):
        j = d_Tn - 1 - i
        ci = carries[i] if i < clen else 0
        cj = carries[j] if 0 <= j < clen else 0
        A_carry_twice += abs(ci - cj)  # this equals 2 * (0.5 * abs(ci-cj))

    # overflow addition as in original: if d_Tn > d_n then +1 (which corresponds to +2 in doubled metric)
    if d_Tn > d_n:
        A_carry_twice += 2  # corresponds to +1 when dividing by 2

    # convert back to float-like value for compatibility (div by 2)
    A_carry_Tn = A_carry_twice / 2.0

    A_robust_n = A_ext_n + A_int_n
    A_robust_Tn = A_ext_Tn + A_int_Tn + A_carry_Tn

    return {
        'n': {'A_ext': A_ext_n, 'A_int': A_int_n, 'A_robust': A_robust_n},
        'T_n': {'A_ext': A_ext_Tn, 'A_int': A_int_Tn, 'A_carry': A_carry_Tn, 'A_robust': A_robust_Tn},
        'deltas': {'Delta_ext': A_ext_n - A_ext_Tn, 'Delta_int': A_int_Tn - A_int_n, 'Delta_carry': A_carry_Tn}
    }


# -------------------------
# GAP 2: obstruction mod 2 (VERSION DETERMINISTE O(d))
# -------------------------
def check_palindrome_obstruction_mod2_fast(n: int) -> Tuple[bool, Optional[List[int]]]:
    """
    Implémentation optimisée du test MOD 2:
    Simule l'addition n + rev(n) en déterminant les retenues successives;
    si le résultat est un palindrome -> obstruction absente (return False, carries)
    Sinon -> aucune assignation valide qui fasse palindrome (return True, None)
    REMARQUE: ceci reprend la logique correcte pour l'addition base 10.
    """
    digits = number_to_digits_int(n)
    d = len(digits)
    carries = [0] * (d + 1)
    result_digits = [0] * (d + 1)

    # simuler et déterminer retenues
    for i in range(d):
        j = d - 1 - i
        s = digits[i] + digits[j] + carries[i]
        result_digits[i] = s % 10
        carries[i + 1] = s // 10

    # gérer overflow
    L = d
    if carries[d] > 0:
        result_digits[d] = carries[d]
        L = d + 1

    # vérif palindrome
    is_pal = True
    for i in range(L // 2):
        if result_digits[i] != result_digits[L - 1 - i]:
            is_pal = False
            break

    if is_pal:
        # obstruction absente (il existe une configuration produisant un palindrome)
        return False, carries[:d+1]
    else:
        # obstruction persistante mod2
        return True, None

# -------------------------
# CLASS UltimateGapTester FAST
# -------------------------
class UltimateGapTesterFast:
    def __init__(self, n0: int = 196, max_iterations: int = 10000, max_digits: int = 1000):
        self.n0 = int(n0)
        self.max_iterations = int(max_iterations)
        self.max_digits = int(max_digits)
        self.results = {
            'config': {
                'n0': self.n0,
                'max_iterations': self.max_iterations,
                'max_digits': self.max_digits,
                'start_time': datetime.now().isoformat()
            },
            'gap1_transfer': {'violations': [], 'statistics': []},
            'gap2_hensel': {'obstructions_found': [], 'checked': 0},
            'gap3_invariance': {'violations': [], 'statistics': []},
            'trajectory': []
        }

    def classify_number(self, A_ext, A_int):
        if A_ext >= 2:
            return "I"
        elif A_ext == 1 and A_int >= 1:
            return "II"
        elif A_ext == 1 and A_int == 0:
            return "II*"
        elif A_ext == 0 and A_int >= 1:
            return "III"
        else:
            return "INVALIDE"

    def test_all_gaps(self, iteration: int, n: int, T_n: int, details: dict):
        result = {
            'iteration': iteration,
            'length': len(str(n)),
            'gap1_ok': True,
            'gap1_tested': False,
            'gap2_ok': True,
            'gap3_ok': True
        }

        # GAP 1
        Delta_ext = details['deltas']['Delta_ext']
        Delta_int = details['deltas']['Delta_int']
        Delta_carry = details['deltas']['Delta_carry']

        if Delta_ext > 0:
            result['gap1_tested'] = True
            expected_transfer = Delta_ext // 2
            actual_transfer = Delta_int + Delta_carry
            if actual_transfer < expected_transfer:
                result['gap1_ok'] = False
                self.results['gap1_transfer']['violations'].append({
                    'iteration': iteration,
                    'Delta_ext': Delta_ext,
                    'expected': expected_transfer,
                    'actual': actual_transfer,
                    'deficit': expected_transfer - actual_transfer
                })
            self.results['gap1_transfer']['statistics'].append({
                'iteration': iteration,
                'Delta_ext': Delta_ext,
                'transfer': actual_transfer,
                'ratio': (actual_transfer / Delta_ext) if Delta_ext != 0 else None,
                'verified': actual_transfer >= expected_transfer
            })

        # GAP 2 (Hensel mod 2) - deterministic O(d)
        has_obstruction, carries_cfg = check_palindrome_obstruction_mod2_fast(n)
        self.results['gap2_hensel']['checked'] += 1
        if not has_obstruction:
            result['gap2_ok'] = False
            self.results['gap2_hensel']['obstructions_found'].append({
                'iteration': iteration,
                'number': n,
                'carries': carries_cfg
            })

        # GAP 3 (invariance trajectoire)
        A_ext_n = details['n']['A_ext']
        A_int_n = details['n']['A_int']
        A_ext_Tn = details['T_n']['A_ext']
        A_int_Tn = details['T_n']['A_int']

        in_validated_class = (A_ext_n >= 1) or (A_int_n >= 1)
        if not in_validated_class:
            result['gap3_ok'] = False
            self.results['gap3_invariance']['violations'].append({
                'iteration': iteration,
                'A_ext': A_ext_n,
                'A_int': A_int_n,
                'message': 'Sorti des classes validées'
            })

        self.results['gap3_invariance']['statistics'].append({
            'iteration': iteration,
            'A_ext_n': A_ext_n,
            'A_int_n': A_int_n,
            'A_ext_Tn': A_ext_Tn,
            'A_int_Tn': A_int_Tn,
            'class': self.classify_number(A_ext_n, A_int_n)
        })

        return result

    def compute_statistics(self):
        gap1_stats = self.results['gap1_transfer']['statistics']
        if gap1_stats:
            valid_stats = [s for s in gap1_stats if s['Delta_ext'] > 0]
            if valid_stats:
                transfers = [s['transfer'] for s in valid_stats]
                deltas = [s['Delta_ext'] for s in valid_stats]
                verified_count = sum(1 for s in valid_stats if s['verified'])
                self.results['gap1_transfer']['summary'] = {
                    'violations': len(self.results['gap1_transfer']['violations']),
                    'total_tested': len(valid_stats),
                    'total_verified': verified_count,
                    'success_rate': (verified_count / len(valid_stats) * 100) if len(valid_stats) else 0,
                    'avg_transfer': sum(transfers) / len(transfers),
                    'avg_delta': sum(deltas) / len(deltas),
                    'min_ratio': min(s['ratio'] for s in valid_stats if s['ratio'] is not None),
                    'avg_ratio': sum(s['ratio'] for s in valid_stats if s['ratio'] is not None) / len(valid_stats)
                }

        # gap3 distribution
        gap3_stats = self.results['gap3_invariance']['statistics']
        class_distribution = {}
        for stat in gap3_stats:
            cls = stat['class']
            class_distribution[cls] = class_distribution.get(cls, 0) + 1
        self.results['gap3_invariance']['class_distribution'] = class_distribution

    def print_comprehensive_report(self):
        # short human summary
        cfg = self.results['config']
        elapsed = cfg.get('elapsed_seconds', None)
        print()
        print("=== FIN DU TEST 3 GAPS - RÉSUMÉ ===")
        if elapsed is not None:
            print(f"Durée totale : {elapsed:.2f} s")
        print(f"Itérations testées : {self.max_iterations + 1}")
        g1v = len(self.results['gap1_transfer']['violations'])
        g2v = len(self.results['gap2_hensel']['obstructions_found'])
        g3v = len(self.results['gap3_invariance']['violations'])

        if g1v == 0:
            print("GAP1: Aucune violation détectée")
        else:
            print(f"GAP1: {g1v} violation(s) détectée(s)")

        if g2v == 0:
            print("GAP2: Aucune solution palindromique mod2 trouvée (obstruction persistante)")
        else:
            print(f"GAP2: {g2v} solution(s) palindromique(s) trouvée(s) — examiner 'gap2_hensel.obstructions_found'")

        if g3v == 0:
            print("GAP3: Trajectoire restée dans classes validées")
        else:
            print(f"GAP3: {g3v} sorties des classes validées")

    def save_results(self):
        fname = f"test_3gaps_fast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"Résultats sauvegardés -> {fname}")

    def run(self):
        print("=== TEST 3 GAPS FAST ===")
        print(f"Nombre initial: {self.n0}  |  Itérations max: {self.max_iterations}  |  Chiffres max: {self.max_digits}")
        start = time.time()
        current = self.n0

        for iteration in range(self.max_iterations + 1):
            T_current, carries, details = apply_T_with_details_int(current)
            r = self.test_all_gaps(iteration, current, T_current, details)
            self.results['trajectory'].append(r)

            # vérif arrêt si chiffres max atteints
            if len(str(current)) > self.max_digits:
                print(f"Arrêt anticipé : longueur de chiffres > {self.max_digits} atteinte à itération {iteration}")
                break

            # affichage léger
            if (iteration < 10) or (iteration % 10 == 0) or (not r['gap1_ok'] or not r['gap2_ok'] or not r['gap3_ok']):
                status1 = "✓" if r['gap1_ok'] else "✗"
                status2 = "✓" if r['gap2_ok'] else "✗"
                status3 = "✓" if r['gap3_ok'] else "✗"
                if not r.get('gap1_tested', True):
                    status1 = "-"
                elapsed = time.time() - start
                rate = (iteration + 1) / elapsed if elapsed > 0 else 0.0
                eta = (self.max_iterations - iteration) / rate if rate > 0 else float('inf')
                print(f"[{iteration:4d}/{self.max_iterations}] GAP1:{status1} GAP2:{status2} GAP3:{status3} | d={len(str(current))} | {rate:.2f} it/s | ETA ~ {eta/60:.2f} min")

                if not r['gap1_ok']:
                    print(f"  ⚠ GAP1 violation it={iteration}")
                if not r['gap2_ok']:
                    print(f"  ⚠ GAP2 obstruction absent it={iteration} (palindrome mod2 trouvé)")
                if not r['gap3_ok']:
                    print(f"  ⚠ GAP3 violation it={iteration}")

            # next
            if iteration < self.max_iterations:
                current = T_current

        # finalisation
        end = time.time()
        self.results['config']['end_time'] = datetime.now().isoformat()
        self.results['config']['elapsed_seconds'] = end - start
        self.compute_statistics()
        self.print_comprehensive_report()
        self.save_results()


# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Test 3 GAPS FAST pour Lychrel (196).")
    parser.add_argument("--n0", type=int, default=196, help="Nombre initial (default: 196)")
    parser.add_argument("--iterations", type=int, default=10000, help="Nombre d'itérations (default:10000)")
    parser.add_argument("--max_digits", type=int, default=1000, help="Longueur max de chiffres pour arrêt anticipé (default:1000)")
    parser.add_argument("--numba", action="store_true", help="Activer numba si disponible (optionnel)")
    args = parser.parse_args()

    if args.numba:
        try:
            import numba  # pragma: no cover
            print("Numba disponible — mais le script principal utilise déjà des opérations entières rapides.")
        except Exception as e:
            print("Numba non disponible ou échec import — continuer sans numba.")

    tester = UltimateGapTesterFast(n0=args.n0, max_iterations=args.iterations, max_digits=args.max_digits)
    tester.run()

if __name__ == "__main__":
    main()
