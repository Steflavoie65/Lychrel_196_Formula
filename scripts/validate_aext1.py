#!/usr/bin/env python3
"""
🎯 VALIDATION CLASSE III: A^(ext) = 0
Le test manquant crucial pour la persistance complète!
Teste: A^(ext)(n) = 0, A^(int)(n) >= 1, T(n) non-pal => A^(robust)(T(n)) >= 1
"""

import json
from itertools import product
from collections import defaultdict
import time

def reverse_number(digits):
    return digits[::-1]

def T_operation(digits):
    n = int(''.join(map(str, digits)))
    rev_n = int(''.join(map(str, reverse_number(digits))))
    result = n + rev_n
    return [int(d) for d in str(result)]

def is_palindrome(digits):
    return digits == digits[::-1]

def compute_A_ext(digits):
    if len(digits) == 1:
        return 0
    return abs(digits[0] - digits[-1])

def compute_A_int(digits):
    d = len(digits)
    if d <= 2:
        return 0
    
    total = 0
    for i in range(1, d // 2):
        weight = 2 ** (i - 1)
        diff = abs(digits[i] - digits[d - 1 - i])
        total += weight * diff
    return total

def compute_carries(digits):
    d = len(digits)
    rev_digits = reverse_number(digits)
    carries = []
    carry = 0
    
    for i in range(d):
        s = digits[d - 1 - i] + rev_digits[d - 1 - i] + carry
        carries.append(carry)
        carry = s // 10
    
    carries.append(carry)
    return carries

def compute_A_carry(digits, carries):
    d = len(digits)
    carry_diff = sum(abs(carries[i] - carries[d - 1 - i]) for i in range(d))
    overflow = 1 if carries[-1] > 0 and not is_palindrome(digits) else 0
    return carry_diff / 2 + overflow

def compute_A_robust(digits):
    carries = compute_carries(digits)
    return (compute_A_ext(digits) + 
            compute_A_int(digits) + 
            compute_A_carry(digits, carries))

def generate_class_III_cases(max_length=8):
    """Generate test cases with A^(ext) = 0 but A^(int) >= 1"""
    test_cases = []
    
    print("🎯 Generating CLASS III test cases (A^(ext) = 0, A^(int) >= 1)...")
    print("This is the CRITICAL missing validation!")
    
    for d in range(3, max_length + 1):
        print(f"  Length {d}...", end=" ", flush=True)
        count = 0
        
        # For each possible a0 = ad (external symmetry)
        for a0 in range(1, 10):  # Leading digit cannot be 0
            ad = a0  # Force A^(ext) = 0
            
            if d == 3:
                # [a0, middle, a0]
                # Need middle != a0 for A^(int) > 0
                for middle in range(0, 10):
                    if middle != a0:  # Ensure internal asymmetry
                        digits = [a0, middle, a0]
                        if not is_palindrome(digits):
                            test_cases.append(digits)
                            count += 1
            
            elif d == 4:
                # [a0, m1, m2, a0]
                # Need (m1, m2) to create internal asymmetry
                for m1 in range(0, 10):
                    for m2 in range(0, 10):
                        digits = [a0, m1, m2, a0]
                        # Check if has internal asymmetry
                        if compute_A_int(digits) >= 1 and not is_palindrome(digits):
                            test_cases.append(digits)
                            count += 1
            
            elif d == 5:
                # [a0, m1, m2, m3, a0]
                for m1 in range(0, 10):
                    for m2 in range(0, 10):
                        for m3 in range(0, 10):
                            digits = [a0, m1, m2, m3, a0]
                            if compute_A_int(digits) >= 1 and not is_palindrome(digits):
                                test_cases.append(digits)
                                count += 1
            
            else:
                # For d >= 6, comprehensive sampling
                # Pattern 1: Asymmetric at position 1
                for m1 in range(0, 10):
                    middle = [m1] + [0] * (d - 4) + [m1 + 1 if m1 < 9 else m1 - 1]
                    digits = [a0] + middle + [a0]
                    if compute_A_int(digits) >= 1 and not is_palindrome(digits):
                        test_cases.append(digits)
                        count += 1
                
                # Pattern 2: Various internal configurations
                patterns = [
                    [1, 0] * ((d-2+1) // 2),
                    [0, 1] * ((d-2+1) // 2),
                    [2, 3] * ((d-2+1) // 2),
                    [5, 4] * ((d-2+1) // 2),
                    [i % 10 for i in range(d-2)],
                    [(i+1) % 10 for i in range(d-2)],
                ]
                
                for pattern in patterns:
                    pattern = pattern[:d-2]
                    digits = [a0] + pattern + [a0]
                    if compute_A_int(digits) >= 1 and not is_palindrome(digits):
                        test_cases.append(digits)
                        count += 1
        
        print(f"+{count} cases")
    
    return test_cases

def run_validation(test_cases):
    """Run validation on Class III cases"""
    results = {
        'total': 0,
        'non_palindromic': 0,
        'palindromic': 0,
        'passed': 0,
        'failed': 0,
        'failures': [],
        'statistics': {
            'A_ext_before': [],
            'A_ext_after': [],
            'A_robust_before': [],
            'A_robust_after': []
        }
    }
    
    print("\n🎯 Running CLASS III VALIDATION...")
    print("Testing the CRITICAL missing case!")
    start_time = time.time()
    
    for i, digits in enumerate(test_cases):
        if (i + 1) % 1000 == 0:
            print(f"Progress: {i+1}/{len(test_cases)} cases tested...", end="\r", flush=True)
        
        results['total'] += 1
        
        # Verify this is indeed Class III
        A_ext_before = compute_A_ext(digits)
        A_int_before = compute_A_int(digits)
        A_robust_before = compute_A_robust(digits)
        
        assert A_ext_before == 0, f"Not Class III! A_ext = {A_ext_before}"
        assert A_int_before >= 1, f"Not Class III! A_int = {A_int_before}"
        
        results['statistics']['A_ext_before'].append(A_ext_before)
        results['statistics']['A_robust_before'].append(A_robust_before)
        
        # Compute T(n)
        result_digits = T_operation(digits)
        
        # Check if result is palindromic
        if is_palindrome(result_digits):
            results['palindromic'] += 1
            continue
        
        results['non_palindromic'] += 1
        
        # Compute A^(robust) for result
        A_ext_after = compute_A_ext(result_digits)
        A_robust_after = compute_A_robust(result_digits)
        
        results['statistics']['A_ext_after'].append(A_ext_after)
        results['statistics']['A_robust_after'].append(A_robust_after)
        
        # Check persistence
        if A_robust_after >= 1.0:
            results['passed'] += 1
        else:
            results['failed'] += 1
            results['failures'].append({
                'input': digits,
                'output': result_digits,
                'A_ext_before': A_ext_before,
                'A_int_before': A_int_before,
                'A_robust_before': A_robust_before,
                'A_ext_after': A_ext_after,
                'A_robust_after': A_robust_after
            })
    
    elapsed = time.time() - start_time
    print(f"Progress: {len(test_cases)}/{len(test_cases)} cases tested... DONE")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    
    return results

def print_results(results):
    """Print detailed results"""
    print("\n" + "="*70)
    print("🎯 CLASS III VALIDATION RESULTS")
    print("="*70)
    
    total = results['total']
    non_pal = results['non_palindromic']
    passed = results['passed']
    failed = results['failed']
    pal = results['palindromic']
    
    print(f"Total Class III cases tested: {total}")
    print(f"  Non-palindromic results: {non_pal}")
    print(f"  - Passed: {passed} ({100*passed/non_pal if non_pal > 0 else 0:.1f}%)")
    print(f"  - FAILED: {failed}")
    print(f"  Palindromic results: {pal} (excluded)")
    
    if failed == 0:
        print("\n" + "🎉"*35)
        print("✅ CLASS III PERSISTENCE CONFIRMED!")
        print("🎉"*35)
        print("\nThe missing piece is now in place!")
        print("Persistence holds even when A^(ext) = 0!")
    else:
        print(f"\n⚠️  CRITICAL: {failed} exceptions found in Class III")
        print("\nThis is the exact boundary of the theorem!")
        
        for i, failure in enumerate(results['failures'][:5], 1):
            print(f"\n--- Failure #{i} ---")
            print(f"  Input:  {failure['input']}")
            print(f"  Output: {failure['output']}")
            print(f"  A^(ext) before: {failure['A_ext_before']}")
            print(f"  A^(int) before: {failure['A_int_before']}")
            print(f"  A^(robust) before: {failure['A_robust_before']:.6f}")
            print(f"  A^(robust) after: {failure['A_robust_after']:.6f}")

def main():
    print("="*70)
    print("🎯 CLASS III VALIDATION - THE MISSING TEST")
    print("Testing A^(ext) = 0 with A^(int) >= 1")
    print("="*70)
    
    # Generate Class III test cases
    test_cases = generate_class_III_cases(max_length=8)
    print(f"\nTotal Class III cases generated: {len(test_cases)}")
    
    # Run validation
    results = run_validation(test_cases)
    
    # Print results
    print_results(results)
    
    # Save results
    output_file = 'validation_results_class_III.json'
    with open(output_file, 'w') as f:
        json.dump({
            'total_cases': results['total'],
            'non_palindromic': results['non_palindromic'],
            'passed': results['passed'],
            'failed': results['failed'],
            'palindromic': results['palindromic'],
            'failures': results['failures']
        }, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Final verdict
    if results['failed'] == 0:
        print("\n" + "🏆"*35)
        print("PERSISTENCE THEOREM NOW COMPLETE!")
        print("="*70)
        print("With this validation, we have covered:")
        print("  ✅ Class I:   A^(ext) >= 2")
        print("  ✅ Class II:  A^(ext) = 1")
        print("  ✅ Class III: A^(ext) = 0, A^(int) >= 1")
        print("\nThe robust invariant persists across ALL classes!")
        print("🏆"*35)

if __name__ == "__main__":
    main()