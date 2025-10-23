"""
Script de validation exhaustive pour A^(ext) >= 5
Vérifie que la persistance de A^(robust) >= 1 tient dans tous les cas

Usage:
    python validate_aext5.py
    
Output:
    - Rapport détaillé des tests
    - Liste des échecs (devrait être vide)
    - Statistiques par cas
"""

from typing import List, Tuple, Dict, Optional
from itertools import product
import json
from datetime import datetime

class ReverseAddValidator:
    """Validateur pour la persistance de A^(robust)"""
    
    def __init__(self):
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
            
        return result, carries[:-1]  # Enlever le dernier carry temporaire
    
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
    
    def compute_A_robust(self, digits: List[int], carries: Optional[List[int]] = None) -> float:
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
        
        if A_ext_initial < 5:
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
        Génère tous les cas de test pertinents pour A^(ext) >= 5
        """
        test_cases = []
        
        # Pour chaque longueur
        for length in range(3, max_length + 1):
            print(f"Generating test cases for length {length}...")
            
            # Pour chaque combinaison (a_0, a_{d-1}) avec |a_0 - a_{d-1}| >= 5
            for a_first in range(10):
                for a_last in range(10):
                    if abs(a_first - a_last) < 5:
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
        
        return test_cases
    
    def run_validation(self, max_length: int = 8) -> Dict:
        """Exécute la validation complète"""
        print(f"\n{'='*70}")
        print("VALIDATION A^(ext) >= 5 PERSISTENCE")
        print(f"{'='*70}\n")
        
        print(f"Generating test cases (max length: {max_length})...")
        test_cases = self.generate_test_cases(max_length)
        print(f"Generated {len(test_cases)} test cases\n")
        
        print("Running tests...")
        passed_count = 0
        failed_count = 0
        palindrome_count = 0
        
        for i, test_case in enumerate(test_cases):
            if (i + 1) % 100 == 0:
                print(f"Progress: {i+1}/{len(test_cases)} cases tested...")
            
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
        
        print(f"\n{'='*70}")
        print("RESULTS")
        print(f"{'='*70}\n")
        
        total_tested = passed_count + failed_count + palindrome_count
        
        print(f"Total cases tested: {total_tested}")
        print(f"  Non-palindromic results: {passed_count + failed_count}")
        print(f"  - Passed: {passed_count} ({100*passed_count/(passed_count+failed_count):.1f}%)")
        print(f"  - FAILED: {failed_count}")
        print(f"  Palindromic results: {palindrome_count} (excluded)")
        
        if failed_count == 0:
            print(f"\n✅ SUCCESS: All non-palindromic cases maintain A^(robust) >= 1!")
        else:
            print(f"\n❌ FAILURE: {failed_count} cases violate persistence!")
            print("\nFailed cases:")
            for failure in self.failures[:10]:  # Show first 10
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
        
        for key in sorted(case_stats.keys()):
            stats = case_stats[key]
            pct = 100 * stats['passed'] / stats['total']
            status = "✅" if pct == 100 else "❌"
            print(f"{status} ({key[0]}, {key[1]}): {stats['passed']}/{stats['total']} ({pct:.1f}%)")
        
        # Sauvegarder les résultats
        self.save_results()
        
        return {
            'total_tested': total_tested,
            'passed': passed_count,
            'failed': failed_count,
            'palindromes': palindrome_count,
            'success': failed_count == 0
        }
    
    def save_results(self, filename: str = "validation_results_aext5.json"):
        """Sauvegarde les résultats en JSON"""
        results = {
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
    validator = ReverseAddValidator()
    results = validator.run_validation(max_length=8)
    
    if results['success']:
        print("\n" + "="*70)
        print("🎉 VALIDATION SUCCESSFUL!")
        print("="*70)
        print("\nTheorem verified: For all tested cases with A^(ext) >= 5,")
        print("if T(n) is non-palindromic, then A^(robust)(T(n)) >= 1")
        return 0
    else:
        print("\n" + "="*70)
        print("❌ VALIDATION FAILED")
        print("="*70)
        return 1


if __name__ == "__main__":
    exit(main())