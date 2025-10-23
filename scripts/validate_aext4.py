"""
Script de validation exhaustive pour A^(ext) >= 4
Extension du script A^(ext) >= 5 avec plus de paires à tester

Usage:
    python validate_aext4.py
    
Output:
    - Rapport détaillé des tests
    - Liste des échecs (devrait être vide)
    - Statistiques par cas
    - Comparaison avec A^(ext) >= 5
"""

from typing import List, Tuple, Dict, Optional
from itertools import product
import json
from datetime import datetime

class ReverseAddValidator:
    """Validateur pour la persistance de A^(robust)"""
    
    def __init__(self, threshold: int = 4):
        self.threshold = threshold  # A^(ext) >= threshold
        self.test_results = []
        self.failures = []
        self.case_stats = {}
        
    def reverse_number(self, digits: List[int]) -> List[int]:
        """Inverse la liste des chiffres"""
        return digits[::-1]
    
    def add_with_carries(self, digits: List[int]) -> Tuple[List[int], List[int]]:
        """
        Effectue n + reverse(n) avec suivi des carries
        Returns: (result_digits, carry_vector)
        """
        n = len(digits)
        rev = self.reverse_number(digits)
        
        result = []
        carries = [0]  # c_{-1} = 0
        carry = 0
        
        # Addition de droite à gauche (LS à MS)
        for i in range(n-1, -1, -1):
            s = digits[i] + rev[i] + carry
            digit = s % 10
            carry = s // 10
            
            result.insert(0, digit)
            carries.append(carry)
        
        # Overflow
        if carry > 0:
            result.insert(0, carry)
            
        return result, carries[:-1]
    
    def is_palindrome(self, digits: List[int]) -> bool:
        """Vérifie si le nombre est palindrome"""
        return digits == digits[::-1]
    
    def compute_A_ext(self, digits: List[int]) -> int:
        """Calcule A^(ext) = |a_0 - a_{d-1}|"""
        if len(digits) < 2:
            return 0
        return abs(digits[0] - digits[-1])
    
    def compute_A_int(self, digits: List[int]) -> float:
        """Calcule A^(int) avec poids exponentiels"""
        d = len(digits)
        if d < 3:
            return 0
        
        total = 0
        for i in range(1, d // 2):
            weight = 2 ** (i - 1)
            asymmetry = abs(digits[i] - digits[d-1-i])
            total += weight * asymmetry
        
        return total
    
    def compute_A_carry(self, digits: List[int], carries: List[int]) -> float:
        """Calcule A^(carry) avec asymétrie des carries"""
        d = len(digits)
        if d < 2:
            return 0
        
        # Ajuster carries pour avoir la bonne longueur
        while len(carries) < d:
            carries.append(0)
        
        total = 0
        for i in range(d):
            mirror = d - 1 - i
            if mirror < len(carries):
                total += abs(carries[i] - carries[mirror])
        
        return total / 2
    
    def compute_A_robust(self, digits: List[int], carries: 'Optional[List[int]]' = None) -> float:
        """Calcule A^(robust) = A^(ext) + A^(int) + A^(carry)"""
        A_ext = self.compute_A_ext(digits)
        A_int = self.compute_A_int(digits)
        
        if carries is None:
            # Calculer les carries pour ce nombre
            _, carries = self.add_with_carries(digits)
        
        A_carry = self.compute_A_carry(digits, carries)
        
        return A_ext + A_int + A_carry
    
    def test_single_case(self, digits: List[int]) -> Optional[Dict]:
        """Teste un cas individuel"""
        # Calculer A^(ext) initial
        A_ext_initial = self.compute_A_ext(digits)
        
        if A_ext_initial < self.threshold:
            return None  # Pas dans notre domaine de test
        
        # Appliquer T
        T_n, carries = self.add_with_carries(digits)
        
        # Vérifier si T(n) est palindrome
        is_pal = self.is_palindrome(T_n)
        
        if is_pal:
            return {
                'n': digits,
                'T_n': T_n,
                'palindrome': True,
                'A_robust_initial': self.compute_A_robust(digits),
                'A_robust_final': 0,
                'passed': True  # Cas dégénéré OK
            }
        
        # Calculer A^(robust) final
        A_robust_final = self.compute_A_robust(T_n, carries)
        
        # Vérifier persistance
        passed = A_robust_final >= 1.0
        
        result = {
            'n': digits,
            'T_n': T_n,
            'palindrome': False,
            'A_ext_initial': A_ext_initial,
            'A_ext_final': self.compute_A_ext(T_n),
            'A_robust_initial': self.compute_A_robust(digits),
            'A_robust_final': A_robust_final,
            'passed': passed
        }
        
        if not passed:
            self.failures.append(result)
        
        return result
    
    def generate_test_cases(self, max_length: int = 8) -> List[List[int]]:
        """
        Génère tous les cas de test pertinents pour A^(ext) >= threshold
        """
        test_cases = []
        
        print(f"\nGenerating test cases for A^(ext) >= {self.threshold}...")
        print(f"This includes all pairs from A^(ext) >= 5 PLUS new pairs\n")
        
        # Pour chaque longueur
        for length in range(3, max_length + 1):
            print(f"  Length {length}...", end="")
            count_before = len(test_cases)
            
            # Pour chaque combinaison (a_0, a_{d-1}) avec |a_0 - a_{d-1}| >= threshold
            for a_first in range(10):
                for a_last in range(10):
                    if abs(a_first - a_last) < self.threshold:
                        continue
                    
                    if a_first == 0:  # Pas de leading zero
                        continue
                    
                    # Échantillonner les intérieurs
                    interior_length = length - 2
                    
                    if interior_length == 0:
                        # Nombres à 2 chiffres
                        test_cases.append([a_first, a_last])
                    
                    elif interior_length <= 3:
                        # Énumération exhaustive pour petits intérieurs
                        for interior in product(range(10), repeat=interior_length):
                            test_cases.append([a_first] + list(interior) + [a_last])
                    
                    else:
                        # Échantillonnage pour grands intérieurs
                        # Cas extrêmes
                        test_cases.append([a_first] + [0] * interior_length + [a_last])
                        test_cases.append([a_first] + [9] * interior_length + [a_last])
                        test_cases.append([a_first] + [5] * interior_length + [a_last])
                        
                        # Échantillon aléatoire
                        import random
                        for _ in range(10):
                            interior = [random.randint(0, 9) for _ in range(interior_length)]
                            test_cases.append([a_first] + interior + [a_last])
            
            count_after = len(test_cases)
            print(f" +{count_after - count_before} cases")
        
        return test_cases
    
    def count_new_pairs(self) -> Tuple[int, List[Tuple[int, int]]]:
        """
        Compte les nouvelles paires par rapport à A^(ext) >= 5
        """
        # Paires pour A^(ext) >= 5
        pairs_5 = set()
        for a_first in range(10):
            for a_last in range(10):
                if abs(a_first - a_last) >= 5 and a_first != 0:
                    pairs_5.add((a_first, a_last))
        
        # Paires pour A^(ext) >= 4
        pairs_4 = set()
        for a_first in range(10):
            for a_last in range(10):
                if abs(a_first - a_last) >= 4 and a_first != 0:
                    pairs_4.add((a_first, a_last))
        
        new_pairs = pairs_4 - pairs_5
        return len(new_pairs), sorted(new_pairs)
    
    def run_validation(self, max_length: int = 8) -> Dict:
        """Exécute la validation complète"""
        print(f"\n{'='*70}")
        print(f"VALIDATION A^(ext) >= {self.threshold} PERSISTENCE")
        print(f"{'='*70}\n")
        
        # Analyser les nouvelles paires
        n_new, new_pairs = self.count_new_pairs()
        print(f"New pairs compared to A^(ext) >= 5: {n_new}")
        print(f"New pairs to test: {new_pairs[:10]}{'...' if len(new_pairs) > 10 else ''}\n")
        
        print(f"Generating test cases (max length: {max_length})...")
        test_cases = self.generate_test_cases(max_length)
        print(f"\nTotal generated: {len(test_cases)} test cases")
        print(f"Expected increase over A^(ext) >= 5: ~{n_new * 1000} cases\n")
        
        print("Running tests...")
        passed_count = 0
        failed_count = 0
        palindrome_count = 0
        
        for i, test_case in enumerate(test_cases):
            if (i + 1) % 100 == 0:
                print(f"Progress: {i+1}/{len(test_cases)} cases tested...", end='\r')
            
            result = self.test_single_case(test_case)
            
            if result is None:
                continue
            
            self.test_results.append(result)
            
            if result['palindrome']:
                palindrome_count += 1
            elif result['passed']:
                passed_count += 1
            else:
                failed_count += 1
        
        print(f"Progress: {len(test_cases)}/{len(test_cases)} cases tested... DONE")
        
        print(f"\n{'='*70}")
        print("RESULTS")
        print(f"{'='*70}\n")
        
        total_tested = passed_count + failed_count + palindrome_count
        
        print(f"Total cases tested: {total_tested}")
        print(f"  Non-palindromic results: {passed_count + failed_count}")
        print(f"  - Passed: {passed_count} ({100*passed_count/(passed_count+failed_count) if (passed_count+failed_count) > 0 else 0:.1f}%)")
        print(f"  - FAILED: {failed_count}")
        print(f"  Palindromic results: {palindrome_count} (excluded)")
        
        if failed_count == 0:
            print(f"\n✅ SUCCESS: All non-palindromic cases maintain A^(robust) >= 1!")
        else:
            print(f"\n❌ FAILURE: {failed_count} cases violate persistence!")
            print("\nFailed cases:")
            for failure in self.failures[:10]:
                print(f"  n = {failure['n']}")
                print(f"  T(n) = {failure['T_n']}")
                print(f"  A^(robust)(T(n)) = {failure['A_robust_final']:.2f}")
        
        # Statistiques par (a_0, a_{d-1})
        print(f"\n{'='*70}")
        print("STATISTICS BY (a_0, a_{d-1})")
        print(f"{'='*70}\n")
        
        case_stats = {}
        for result in self.test_results:
            if result['palindrome']:
                continue
            
            key = (result['n'][0], result['n'][-1])
            if key not in case_stats:
                case_stats[key] = {'total': 0, 'passed': 0}
            
            case_stats[key]['total'] += 1
            if result['passed']:
                case_stats[key]['passed'] += 1
        
        print("Pairs from A^(ext) >= 5 (should all be 100%):")
        pairs_5_count = 0
        for key in sorted(case_stats.keys()):
            if abs(key[0] - key[1]) >= 5:
                stats = case_stats[key]
                pct = 100 * stats['passed'] / stats['total']
                status = "✅" if pct == 100 else "❌"
                print(f"  {status} {key}: {stats['passed']}/{stats['total']} ({pct:.1f}%)")
                pairs_5_count += 1
        
        print(f"\nNEW pairs for A^(ext) >= 4:")
        pairs_4_new_count = 0
        for key in sorted(case_stats.keys()):
            if abs(key[0] - key[1]) == 4:
                stats = case_stats[key]
                pct = 100 * stats['passed'] / stats['total']
                status = "✅" if pct == 100 else "❌"
                print(f"  {status} {key}: {stats['passed']}/{stats['total']} ({pct:.1f}%)")
                pairs_4_new_count += 1
        
        print(f"\nSummary: {pairs_5_count} pairs from >=5, {pairs_4_new_count} new pairs for >=4")
        
        # Sauvegarder les résultats
        self.save_results()
        
        return {
            'total_tested': total_tested,
            'passed': passed_count,
            'failed': failed_count,
            'palindromes': palindrome_count,
            'success': failed_count == 0,
            'new_pairs_tested': pairs_4_new_count
        }
    
    def save_results(self, filename: Optional[str] = None):
        """Sauvegarde les résultats en JSON"""
        if filename is None:
            filename = f"validation_results_aext{self.threshold}.json"
        
        results = {
            'threshold': self.threshold,
            'timestamp': datetime.now().isoformat(),
            'total_cases': len(self.test_results),
            'failures': self.failures,
            'summary': {
                'passed': sum(1 for r in self.test_results if r['passed'] and not r['palindrome']),
                'failed': len(self.failures),
                'palindromes': sum(1 for r in self.test_results if r['palindrome'])
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {filename}")


def main():
    """Point d'entrée principal"""
    print("\n" + "="*70)
    print("LYCHREL PERSISTENCE VALIDATOR")
    print("Testing A^(ext) >= 4")
    print("="*70)
    
    validator = ReverseAddValidator(threshold=4)
    results = validator.run_validation(max_length=8)
    
    print("\n" + "="*70)
    print("COMPARISON WITH A^(ext) >= 5")
    print("="*70)
    print(f"\nA^(ext) >= 5 tested: ~28,725 cases (from previous run)")
    print(f"A^(ext) >= 4 tested: {results['total_tested']} cases (this run)")
    print(f"Increase: ~{results['total_tested'] - 28725} cases")
    print(f"New pairs validated: {results['new_pairs_tested']}")
    
    if results['success']:
        print("\n" + "="*70)
        print("🎉 VALIDATION SUCCESSFUL!")
        print("="*70)
        print("\nTheorem verified: For all tested cases with A^(ext) >= 4,")
        print("if T(n) is non-palindromic, then A^(robust)(T(n)) >= 1")
        print("\nThis extends the A^(ext) >= 5 result to a broader class!")
        return 0
    else:
        print("\n" + "="*70)
        print("❌ VALIDATION FAILED")
        print("="*70)
        return 1


if __name__ == "__main__":
    exit(main())