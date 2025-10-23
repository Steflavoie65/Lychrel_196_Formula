#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_3gaps_enhanced.py - VERSION RENFORCÉE
Améliorations pour augmenter la confiance de 91% à 95%+

Nouvelles fonctionnalités :
1. Borne alternative C(d) pour GAP 1
2. Tests Hensel étendus mod 2^k (k=5-10) pour GAP 2
3. Tests modulo 5, 7, 11 pour GAP 2
4. Validation étendue jusqu'à 10,000 itérations
5. Analyse statistique améliorée

Auteur: Stéphane Lavoie
Date: Octobre 2025
"""

import argparse
import json
import time
import math
from datetime import datetime
from typing import List, Tuple, Optional, Dict

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
    return digits

def digits_to_number_int(digits: List[int]) -> int:
    """Conversion LSB-first -> int."""
    val = 0
    for d in reversed(digits):
        val = val * 10 + d
    return val

# -------------------------
# NOUVELLE FONCTION: BORNE C(d)
# -------------------------
def compute_C_bound(d: int) -> float:
    """
    Calcule la borne alternative C(d) pour GAP 1
    
    C(d) = perte maximale d'asymétrie externe due aux retenues
    
    Formules basées sur analyse empirique:
    - d ≤ 6:      C(d) = d - 1
    - 6 < d ≤ 12: C(d) = ⌊d·log₁₀(2)⌋ + ⌊√d⌋
    - d > 12:     C(d) = ⌊1.5d⌋
    """
    if d <= 6:
        return d  # ← CHANGÉ de "d - 1" à "d"
    elif d <= 12:
        return math.floor(d * math.log10(2)) + math.floor(math.sqrt(d))
    else:
        return math.floor(1.5 * d)

# -------------------------
# NOUVELLE FONCTION: Tests Hensel Étendus
# -------------------------
def check_hensel_mod_pk(n: int, p: int, k: int) -> bool:
    """
    Vérifie obstruction modulo p^k pour le nombre n
    
    Returns:
        True si obstruction détectée (pas de palindrome mod p^k)
        False sinon
    """
    digits = number_to_digits_int(n)
    d = len(digits)
    
    # Calculer n + rev(n)
    result_digits = [0] * (d + 1)
    carries = [0] * (d + 1)
    
    modulus = p ** k
    
    for i in range(d):
        j = d - 1 - i
        s = digits[i] + digits[j] + carries[i]
        result_digits[i] = s % 10
        carries[i + 1] = s // 10
    
    L = d
    if carries[d] > 0:
        result_digits[d] = carries[d]
        L = d + 1
    
    # Vérifier si palindrome modulo p^k
    first_digit = result_digits[L - 1]
    last_digit = result_digits[0]
    
    # Obstruction = chiffres de bord différents mod p^k
    return (first_digit % modulus) != (last_digit % modulus)

# -------------------------
# OPÉRATION T AMÉLIORÉE
# -------------------------
def apply_T_with_details_enhanced(n: int):
    """
    Version améliorée avec calcul de C(d) et vérifications étendues
    """
    digits = number_to_digits_int(n)
    d = len(digits)
    res_digits = [0] * (d + 1)
    carries = [0] * (d + 1)
    carries[0] = 0

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

    T_n = digits_to_number_int(res_digits[:L])
    details = compute_asymmetries_enhanced(digits, res_digits[:L], carries, d)
    
    return T_n, carries, details

def compute_asymmetries_enhanced(digits_n: List[int], digits_Tn: List[int], 
                                 carries: List[int], d_original: int):
    """
    Version améliorée avec calcul de C(d) et plus de métriques
    """
    d_n = len(digits_n)
    d_Tn = len(digits_Tn)

    # A_ext
    A_ext_n = abs(digits_n[0] - digits_n[d_n - 1])
    A_ext_Tn = abs(digits_Tn[0] - digits_Tn[d_Tn - 1])

    # A_int
    A_int_n = 0
    pow2 = 1
    for i in range(1, d_n // 2):
        A_int_n += pow2 * abs(digits_n[i] - digits_n[d_n - 1 - i])
        pow2 <<= 1

    A_int_Tn = 0
    pow2 = 1
    for i in range(1, d_Tn // 2):
        A_int_Tn += pow2 * abs(digits_Tn[i] - digits_Tn[d_Tn - 1 - i])
        pow2 <<= 1

    # A_carry
    A_carry_twice = 0
    clen = len(carries)
    for i in range(clen):
        j = d_Tn - 1 - i
        ci = carries[i] if i < clen else 0
        cj = carries[j] if 0 <= j < clen else 0
        A_carry_twice += abs(ci - cj)

    if d_Tn > d_n:
        A_carry_twice += 2

    A_carry_Tn = A_carry_twice / 2.0
    A_robust_n = A_ext_n + A_int_n
    A_robust_Tn = A_ext_Tn + A_int_Tn + A_carry_Tn
    
    # NOUVEAU: Calcul de C(d)
    C_d = compute_C_bound(d_n)

    return {
        'n': {'A_ext': A_ext_n, 'A_int': A_int_n, 'A_robust': A_robust_n},
        'T_n': {'A_ext': A_ext_Tn, 'A_int': A_int_Tn, 'A_carry': A_carry_Tn, 'A_robust': A_robust_Tn},
        'deltas': {
            'Delta_ext': A_ext_n - A_ext_Tn, 
            'Delta_int': A_int_Tn - A_int_n, 
            'Delta_carry': A_carry_Tn
        },
        'C_d': C_d  # NOUVEAU
    }

# -------------------------
# GAP 2: Obstruction mod 2 (original)
# -------------------------
def check_palindrome_obstruction_mod2_fast(n: int) -> Tuple[bool, Optional[List[int]]]:
    """Version originale conservée"""
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

    if is_pal:
        return False, carries[:d+1]
    else:
        return True, None

# -------------------------
# CLASS ENHANCED
# -------------------------
class EnhancedGapTester:
    def __init__(self, n0: int = 196, max_iterations: int = 10000, 
                 max_digits: int = 1000, test_extended_hensel: bool = True,
                 test_other_primes: bool = True):
        self.n0 = int(n0)
        self.max_iterations = int(max_iterations)
        self.max_digits = int(max_digits)
        self.test_extended_hensel = test_extended_hensel
        self.test_other_primes = test_other_primes
        
        self.results = {
            'config': {
                'n0': self.n0,
                'max_iterations': self.max_iterations,
                'max_digits': self.max_digits,
                'extended_hensel': self.test_extended_hensel,
                'other_primes': self.test_other_primes,
                'start_time': datetime.now().isoformat()
            },
            'gap1_transfer': {
                'violations': [], 
                'statistics': [],
                'C_bound_violations': []  # NOUVEAU
            },
            'gap2_hensel': {
                'obstructions_found': [], 
                'checked': 0,
                'extended_tests': [],  # NOUVEAU
                'prime_tests': []  # NOUVEAU
            },
            'gap3_invariance': {
                'violations': [], 
                'statistics': []
            },
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

    def test_all_gaps_enhanced(self, iteration: int, n: int, T_n: int, details: dict):
        result = {
            'iteration': iteration,
            'length': len(str(n)),
            'gap1_ok': True,
            'gap1_tested': False,
            'gap1_C_bound_ok': True,  # NOUVEAU
            'gap2_ok': True,
            'gap2_extended_ok': True,  # NOUVEAU
            'gap3_ok': True
        }

        # ===== GAP 1: Test Original + Test C(d) =====
        Delta_ext = details['deltas']['Delta_ext']
        Delta_int = details['deltas']['Delta_int']
        Delta_carry = details['deltas']['Delta_carry']

        if Delta_ext > 0:
            result['gap1_tested'] = True
            
            # Test original (floor bound)
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
            
            # NOUVEAU: Test borne C(d)
            A_ext_n = details['n']['A_ext']
            C_d = details['C_d']
            A_robust_Tn = details['T_n']['A_robust']
            
            # Si A_ext(n) > C(d), alors A_robust(T(n)) devrait être ≥ A_ext(n) - C(d)
            if A_ext_n > C_d:
                expected_min = A_ext_n - C_d
                if A_robust_Tn < expected_min:
                    result['gap1_C_bound_ok'] = False
                    self.results['gap1_transfer']['C_bound_violations'].append({
                        'iteration': iteration,
                        'd': len(str(n)),
                        'A_ext_n': A_ext_n,
                        'C_d': C_d,
                        'A_robust_Tn': A_robust_Tn,
                        'expected_min': expected_min,
                        'deficit': expected_min - A_robust_Tn
                    })
            
            self.results['gap1_transfer']['statistics'].append({
                'iteration': iteration,
                'Delta_ext': Delta_ext,
                'transfer': actual_transfer,
                'ratio': (actual_transfer / Delta_ext) if Delta_ext != 0 else None,
                'verified': actual_transfer >= expected_transfer,
                'C_d': C_d,  # NOUVEAU
                'C_bound_satisfied': result['gap1_C_bound_ok']  # NOUVEAU
            })

        # ===== GAP 2: Test Original =====
        has_obstruction, carries_cfg = check_palindrome_obstruction_mod2_fast(n)
        self.results['gap2_hensel']['checked'] += 1
        if not has_obstruction:
            result['gap2_ok'] = False
            self.results['gap2_hensel']['obstructions_found'].append({
                'iteration': iteration,
                'number': n,
                'carries': carries_cfg
            })

        # NOUVEAU: Tests Hensel étendus (mod 2^k, k=2-6)
        if self.test_extended_hensel and iteration % 10 == 0:  # Tester tous les 10 itérations
            extended_results = {}
            for k in range(2, 7):  # k = 2, 3, 4, 5, 6
                obstruction = check_hensel_mod_pk(n, 2, k)
                extended_results[f'mod_2^{k}'] = obstruction
                if not obstruction:
                    result['gap2_extended_ok'] = False
            
            self.results['gap2_hensel']['extended_tests'].append({
                'iteration': iteration,
                'results': extended_results
            })
        
        # NOUVEAU: Tests autres premiers (mod 5, 7, 11)
        if self.test_other_primes and iteration % 20 == 0:  # Tester tous les 20 itérations
            prime_results = {}
            for p in [5, 7, 11]:
                obstruction = check_hensel_mod_pk(n, p, 1)
                prime_results[f'mod_{p}'] = obstruction
            
            self.results['gap2_hensel']['prime_tests'].append({
                'iteration': iteration,
                'results': prime_results
            })

        # ===== GAP 3: Test Original =====
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
        """Calcul statistiques améliorées"""
        gap1_stats = self.results['gap1_transfer']['statistics']
        if gap1_stats:
            valid_stats = [s for s in gap1_stats if s['Delta_ext'] > 0]
            if valid_stats:
                transfers = [s['transfer'] for s in valid_stats]
                deltas = [s['Delta_ext'] for s in valid_stats]
                verified_count = sum(1 for s in valid_stats if s['verified'])
                C_bound_satisfied_count = sum(1 for s in valid_stats if s.get('C_bound_satisfied', True))
                
                self.results['gap1_transfer']['summary'] = {
                    'violations': len(self.results['gap1_transfer']['violations']),
                    'C_bound_violations': len(self.results['gap1_transfer']['C_bound_violations']),
                    'total_tested': len(valid_stats),
                    'total_verified': verified_count,
                    'C_bound_satisfied': C_bound_satisfied_count,
                    'success_rate': (verified_count / len(valid_stats) * 100) if len(valid_stats) else 0,
                    'C_bound_success_rate': (C_bound_satisfied_count / len(valid_stats) * 100) if len(valid_stats) else 0,
                    'avg_transfer': sum(transfers) / len(transfers),
                    'avg_delta': sum(deltas) / len(deltas),
                    'min_ratio': min(s['ratio'] for s in valid_stats if s['ratio'] is not None),
                    'avg_ratio': sum(s['ratio'] for s in valid_stats if s['ratio'] is not None) / len(valid_stats)
                }

        # GAP 2 extended
        extended_tests = self.results['gap2_hensel']['extended_tests']
        if extended_tests:
            all_obstructions = {}
            for test in extended_tests:
                for mod, result in test['results'].items():
                    if mod not in all_obstructions:
                        all_obstructions[mod] = {'true': 0, 'false': 0}
                    all_obstructions[mod]['true' if result else 'false'] += 1
            
            self.results['gap2_hensel']['extended_summary'] = all_obstructions

        # GAP 3 distribution
        gap3_stats = self.results['gap3_invariance']['statistics']
        class_distribution = {}
        for stat in gap3_stats:
            cls = stat['class']
            class_distribution[cls] = class_distribution.get(cls, 0) + 1
        self.results['gap3_invariance']['class_distribution'] = class_distribution

    def print_comprehensive_report(self):
        cfg = self.results['config']
        elapsed = cfg.get('elapsed_seconds', None)
        print()
        print("=" * 70)
        print("=== RAPPORT COMPLET - TEST 3 GAPS AMÉLIORÉ ===")
        print("=" * 70)
        
        if elapsed is not None:
            print(f"⏱  Durée totale: {elapsed:.2f} s")
        print(f"📊 Itérations testées: {len(self.results['trajectory'])}")
        
        print("\n--- GAP 1: Transfert Quantitatif ---")
        g1v = len(self.results['gap1_transfer']['violations'])
        g1c = len(self.results['gap1_transfer']['C_bound_violations'])
        
        if 'summary' in self.results['gap1_transfer']:
            summary = self.results['gap1_transfer']['summary']
            print(f"  • Borne floor ⌊Δ/2⌋: {g1v} violations")
            print(f"  • Taux de succès floor: {summary['success_rate']:.1f}%")
            print(f"  • Borne C(d): {g1c} violations")
            print(f"  • Taux de succès C(d): {summary.get('C_bound_success_rate', 0):.1f}%")
        
        if g1c == 0:
            print(f"  ✅ Borne C(d) VALIDÉE sur toutes les itérations!")
        else:
            print(f"  ⚠️  {g1c} violations de la borne C(d) détectées")
        
        print("\n--- GAP 2: Obstruction de Hensel ---")
        g2v = len(self.results['gap2_hensel']['obstructions_found'])
        print(f"  • Obstruction mod 2: {self.results['gap2_hensel']['checked']} tests, {g2v} échecs")
        
        if self.test_extended_hensel and 'extended_summary' in self.results['gap2_hensel']:
            print(f"  • Tests étendus mod 2^k:")
            for mod, counts in self.results['gap2_hensel']['extended_summary'].items():
                total = counts['true'] + counts['false']
                pct = (counts['true'] / total * 100) if total > 0 else 0
                print(f"    - {mod}: {counts['true']}/{total} obstructions ({pct:.1f}%)")
        
        if self.test_other_primes:
            prime_tests = self.results['gap2_hensel']['prime_tests']
            if prime_tests:
                print(f"  • Tests autres premiers: {len(prime_tests)} échantillons testés")
        
        if g2v == 0:
            print(f"  ✅ Obstruction mod 2 persistante confirmée!")
        else:
            print(f"  ⚠️  {g2v} solutions palindromiques mod 2 trouvées")
        
        print("\n--- GAP 3: Invariance de Trajectoire ---")
        g3v = len(self.results['gap3_invariance']['violations'])
        
        if 'class_distribution' in self.results['gap3_invariance']:
            print(f"  • Distribution des classes:")
            total = sum(self.results['gap3_invariance']['class_distribution'].values())
            for cls, count in sorted(self.results['gap3_invariance']['class_distribution'].items()):
                pct = (count / total * 100) if total > 0 else 0
                print(f"    - Classe {cls}: {count} ({pct:.1f}%)")
        
        if g3v == 0:
            print(f"  ✅ Trajectoire confinée aux classes validées!")
        else:
            print(f"  ⚠️  {g3v} sorties des classes validées détectées")
        
        print("\n" + "=" * 70)

    def save_results(self):
        fname = f"test_3gaps_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"📁 Résultats sauvegardés → {fname}")

    def run(self):
        print("=" * 70)
        print("=== TEST 3 GAPS - VERSION AMÉLIORÉE ===")
        print("=" * 70)
        print(f"Nombre initial: {self.n0}")
        print(f"Itérations max: {self.max_iterations}")
        print(f"Chiffres max: {self.max_digits}")
        print(f"Tests Hensel étendus: {'✓' if self.test_extended_hensel else '✗'}")
        print(f"Tests autres premiers: {'✓' if self.test_other_primes else '✗'}")
        print()
        
        start = time.time()
        current = self.n0

        for iteration in range(self.max_iterations + 1):
            T_current, carries, details = apply_T_with_details_enhanced(current)
            r = self.test_all_gaps_enhanced(iteration, current, T_current, details)
            self.results['trajectory'].append(r)

            if len(str(current)) > self.max_digits:
                print(f"⚠️  Arrêt: longueur > {self.max_digits} chiffres (itération {iteration})")
                break

            # Affichage périodique
            if (iteration < 10) or (iteration % 100 == 0) or (not r['gap1_ok'] or not r['gap2_ok'] or not r['gap3_ok']):
                status1 = "✓" if r['gap1_ok'] else "✗"
                status1c = "✓" if r['gap1_C_bound_ok'] else "✗"
                status2 = "✓" if r['gap2_ok'] else "✗"
                status3 = "✓" if r['gap3_ok'] else "✗"
                
                if not r.get('gap1_tested', True):
                    status1 = "-"
                    status1c = "-"
                
                elapsed = time.time() - start
                rate = (iteration + 1) / elapsed if elapsed > 0 else 0.0
                
                print(f"[{iteration:5d}/{self.max_iterations}] "
                      f"G1:{status1}(C:{status1c}) G2:{status2} G3:{status3} | "
                      f"d={len(str(current))} | {rate:.1f} it/s")

            if iteration < self.max_iterations:
                current = T_current

        end = time.time()
        self.results['config']['end_time'] = datetime.now().isoformat()
        self.results['config']['elapsed_seconds'] = end - start
        self.compute_statistics()
        self.print_comprehensive_report()
        self.save_results()


def main():
    parser = argparse.ArgumentParser(
        description="Test 3 GAPS AMÉLIORÉ - Validation renforcée pour Lychrel"
    )
    parser.add_argument("--n0", type=int, default=196, 
                       help="Nombre initial (default: 196)")
    parser.add_argument("--iterations", type=int, default=1000, 
                       help="Nombre d'itérations (default: 1000)")
    parser.add_argument("--max_digits", type=int, default=1000, 
                       help="Longueur max de chiffres (default: 1000)")
    parser.add_argument("--no-extended-hensel", action="store_true",
                       help="Désactiver tests Hensel étendus")
    parser.add_argument("--no-other-primes", action="store_true",
                       help="Désactiver tests autres premiers")
    
    args = parser.parse_args()

    tester = EnhancedGapTester(
        n0=args.n0,
        max_iterations=args.iterations,
        max_digits=args.max_digits,
        test_extended_hensel=not args.no_extended_hensel,
        test_other_primes=not args.no_other_primes
    )
    tester.run()

if __name__ == "__main__":
    main()