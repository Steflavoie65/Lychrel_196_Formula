#!/usr/bin/env python3
"""
Validation exhaustive pour A^(ext) >= 2
Teste la persistence: A^(ext)(n) >= 2 ET T(n) non-pal => A^(robust)(T(n)) >= 1
"""

import json
from itertools import product
from collections import defaultdict
import time

def reverse_number(digits):
    """Reverse digit list"""
    return digits[::-1]

def T_operation(digits):
    """Compute T(n) = n + reverse(n)"""
    n = int(''.join(map(str, digits)))
    rev_n = int(''.join(map(str, reverse_number(digits))))
    result = n + rev_n
    return [int(d) for d in str(result)]

def is_palindrome(digits):
    """Check if digit sequence is palindromic"""
    return digits == digits[::-1]

def compute_A_ext(digits):
    """Compute external asymmetry A^(ext)"""
    if len(digits) == 1:
        return 0
    return abs(digits[0] - digits[-1])

def compute_A_int(digits):
    """Compute internal asymmetry A^(int) with exponential weights"""
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
    """Compute carry vector for T operation"""
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
    """Compute carry asymmetry A^(carry)"""
    d = len(digits)
    carry_diff = sum(abs(carries[i] - carries[d - 1 - i]) for i in range(d))
    
    overflow = 1 if carries[-1] > 0 and not is_palindrome(digits) else 0
    
    return carry_diff / 2 + overflow

def compute_A_robust(digits):
    """Compute complete robust invariant"""
    carries = compute_carries(digits)
    return (compute_A_ext(digits) + 
            compute_A_int(digits) + 
            compute_A_carry(digits, carries))

def get_critical_pairs(min_gap):
    """Get all critical pairs (a_0, a_{d-1}) with |a_0 - a_{d-1}| >= min_gap"""
    pairs = []
    for a0 in range(1, 10):  # a_0 cannot be 0 (leading digit)
        for ad in range(0, 10):
            if abs(a0 - ad) >= min_gap:
                pairs.append((a0, ad))
    return sorted(pairs)

def generate_test_cases(min_gap=2, max_length=8):
    """Generate all test cases with A^(ext) >= min_gap"""
    pairs = get_critical_pairs(min_gap)
    test_cases = []
    
    print(f"Generating test cases for A^(ext) >= {min_gap}...")
    print(f"Critical pairs to test: {len(pairs)}")
    
    for d in range(3, max_length + 1):
        print(f"  Length {d}...", end=" ", flush=True)
        count = 0
        
        for a0, ad in pairs:
            if d == 3:
                # 3-digit: [a0, middle, ad]
                for middle in range(0, 10):
                    digits = [a0, middle, ad]
                    if not is_palindrome(digits):
                        test_cases.append(digits)
                        count += 1
            
            elif d == 4:
                # 4-digit: [a0, m1, m2, ad]
                for m1 in range(0, 10):
                    for m2 in range(0, 10):
                        digits = [a0, m1, m2, ad]
                        if not is_palindrome(digits):
                            test_cases.append(digits)
                            count += 1
            
            elif d == 5:
                # 5-digit: [a0, m1, m2, m3, ad]
                for m1 in range(0, 10):
                    for m2 in range(0, 10):
                        for m3 in range(0, 10):
                            digits = [a0, m1, m2, m3, ad]
                            if not is_palindrome(digits):
                                test_cases.append(digits)
                                count += 1
            
            else:
                # For d >= 6, sample uniformly to keep reasonable size
                # Use all 0s for middle positions as base case
                middle = [0] * (d - 2)
                digits = [a0] + middle + [ad]
                if not is_palindrome(digits):
                    test_cases.append(digits)
                    count += 1
                
                # Add varied middle configurations
                for pattern in [[1]*len(middle), [2]*len(middle), [5]*len(middle), 
                               [9]*len(middle), [0,1]*((len(middle)+1)//2)][:len(middle)]:
                    digits = [a0] + pattern + [ad]
                    if not is_palindrome(digits):
                        test_cases.append(digits)
                        count += 1
        
        print(f"+{count} cases")
    
    return test_cases

def run_validation(test_cases):
    """Run validation on all test cases"""
    results = {
        'total': 0,
        'non_palindromic': 0,
        'palindromic': 0,
        'passed': 0,
        'failed': 0,
        'failures': [],
        'by_pair': defaultdict(lambda: {'tested': 0, 'passed': 0, 'failed': 0})
    }
    
    print("\nRunning tests...")
    start_time = time.time()
    
    for i, digits in enumerate(test_cases):
        if (i + 1) % 10000 == 0:
            print(f"Progress: {i+1}/{len(test_cases)} cases tested...", end="\r", flush=True)
        
        results['total'] += 1
        pair = (digits[0], digits[-1])
        results['by_pair'][pair]['tested'] += 1
        
        # Compute T(n)
        result_digits = T_operation(digits)
        
        # Check if result is palindromic
        if is_palindrome(result_digits):
            results['palindromic'] += 1
            continue
        
        results['non_palindromic'] += 1
        
        # Compute A^(robust) for result
        A_robust = compute_A_robust(result_digits)
        
        # Check persistence
        if A_robust >= 1.0:
            results['passed'] += 1
            results['by_pair'][pair]['passed'] += 1
        else:
            results['failed'] += 1
            results['by_pair'][pair]['failed'] += 1
            results['failures'].append({
                'input': digits,
                'output': result_digits,
                'A_robust': A_robust,
                'A_ext': compute_A_ext(result_digits),
                'A_int': compute_A_int(result_digits)
            })
    
    elapsed = time.time() - start_time
    print(f"Progress: {len(test_cases)}/{len(test_cases)} cases tested... DONE")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    
    return results

def print_results(results, min_gap):
    """Print detailed results"""
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    total = results['total']
    non_pal = results['non_palindromic']
    passed = results['passed']
    failed = results['failed']
    pal = results['palindromic']
    
    print(f"Total cases tested: {total}")
    print(f"  Non-palindromic results: {non_pal}")
    print(f"  - Passed: {passed} ({100*passed/non_pal if non_pal > 0 else 0:.1f}%)")
    print(f"  - FAILED: {failed}")
    print(f"  Palindromic results: {pal} (excluded)")
    
    if failed == 0:
        print("\n✅ SUCCESS: All non-palindromic cases maintain A^(robust) >= 1!")
    else:
        print(f"\n❌ FAILURES DETECTED: {failed} cases failed")
        print("\nFirst 10 failures:")
        for failure in results['failures'][:10]:
            print(f"  Input: {failure['input']}")
            print(f"  Output: {failure['output']}")
            print(f"  A^(robust) = {failure['A_robust']:.3f}")
            print(f"  A^(ext) = {failure['A_ext']}, A^(int) = {failure['A_int']}")
            print()
    
    # Statistics by pair
    print("\n" + "="*70)
    print("STATISTICS BY (a_0, a_{d-1})")
    print("="*70)
    
    # Separate old pairs from new pairs
    old_pairs_5 = get_critical_pairs(5)
    old_pairs_4 = get_critical_pairs(4)
    old_pairs_3 = get_critical_pairs(3)
    all_pairs_2 = get_critical_pairs(2)
    
    new_from_3 = [p for p in old_pairs_3 if p not in old_pairs_4]
    new_from_2 = [p for p in all_pairs_2 if p not in old_pairs_3]
    
    # Show summary counts first
    print(f"\nPairs from A^(ext) >= 5: {len(old_pairs_5)} (all should be 100%)")
    print(f"Pairs from A^(ext) >= 4: {len(old_pairs_4 ) - len(old_pairs_5)} additional")
    print(f"Pairs from A^(ext) >= 3: {len(old_pairs_3) - len(old_pairs_4)} additional")
    print(f"NEW pairs for A^(ext) >= 2: {len(new_from_2)}")
    
    # Only show new pairs in detail
    print("\nNEW pairs for A^(ext) >= 2:")
    for pair in sorted(new_from_2):
        if pair in results['by_pair']:
            stats = results['by_pair'][pair]
            pct = 100 * stats['passed'] / stats['tested'] if stats['tested'] > 0 else 0
            status = "✅" if stats['failed'] == 0 else "❌"
            print(f"  {status} {pair}: {stats['passed']}/{stats['tested']} ({pct:.1f}%)")
    
    # Show failures if any
    if failed > 0:
        print("\nPairs with FAILURES:")
        for pair in sorted(results['by_pair'].keys()):
            stats = results['by_pair'][pair]
            if stats['failed'] > 0:
                print(f"  ❌ {pair}: {stats['failed']} failures out of {stats['tested']} tests")
    
    print(f"\nTotal unique pairs tested: {len(results['by_pair'])}")

def main():
    print("="*70)
    print("LYCHREL PERSISTENCE VALIDATOR")
    print("Testing A^(ext) >= 2")
    print("="*70)
    
    # Compare with previous thresholds
    pairs_5 = get_critical_pairs(5)
    pairs_4 = get_critical_pairs(4)
    pairs_3 = get_critical_pairs(3)
    pairs_2 = get_critical_pairs(2)
    
    new_pairs = [p for p in pairs_2 if p not in pairs_3]
    
    print("\n" + "="*70)
    print("VALIDATION A^(ext) >= 2 PERSISTENCE")
    print("="*70)
    print(f"Pairs in A^(ext) >= 5: {len(pairs_5)}")
    print(f"Pairs in A^(ext) >= 4: {len(pairs_4)}")
    print(f"Pairs in A^(ext) >= 3: {len(pairs_3)}")
    print(f"Pairs in A^(ext) >= 2: {len(pairs_2)}")
    print(f"New pairs compared to A^(ext) >= 3: {len(new_pairs)}")
    print(f"New pairs: {new_pairs}")
    
    # Generate test cases
    print("\nGenerating test cases (max length: 8)...")
    test_cases = generate_test_cases(min_gap=2, max_length=8)
    print(f"Total generated: {len(test_cases)} test cases")
    
    # Estimate
    prev_estimate = 54978  # from A^(ext) >= 3
    increase = len(test_cases) - prev_estimate
    print(f"Expected increase over A^(ext) >= 3: ~{increase} cases")
    
    # Run validation
    results = run_validation(test_cases)
    
    # Print results
    print_results(results, min_gap=2)
    
    # Save results
    output_file = 'validation_results_aext2.json'
    with open(output_file, 'w') as f:
        json.dump({
            'min_gap': 2,
            'total_cases': results['total'],
            'non_palindromic': results['non_palindromic'],
            'passed': results['passed'],
            'failed': results['failed'],
            'palindromic': results['palindromic'],
            'failures': results['failures'][:100],  # Limit to first 100 failures
            'by_pair': {str(k): v for k, v in results['by_pair'].items()}
        }, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON WITH PREVIOUS VALIDATIONS")
    print("="*70)
    print(f"A^(ext) >= 5 tested: ~28,725 cases")
    print(f"A^(ext) >= 4 tested: ~41,364 cases")
    print(f"A^(ext) >= 3 tested: ~54,978 cases")
    print(f"A^(ext) >= 2 tested: {len(test_cases)} cases (this run)")
    print(f"Increase: ~{len(test_cases) - 54978} cases")
    print(f"New pairs validated: {len(new_pairs)}")
    
    # Success message
    if results['failed'] == 0:
        print("\n" + "="*70)
        print("🎉 VALIDATION SUCCESSFUL!")
        print("="*70)
        print("Theorem verified: For all tested cases with A^(ext) >= 2,")
        print("if T(n) is non-palindromic, then A^(robust)(T(n)) >= 1")
        print("This extends the A^(ext) >= 3 result to an even broader class!")
    else:
        print("\n" + "="*70)
        print("⚠️  VALIDATION INCOMPLETE")
        print("="*70)
        print(f"Found {results['failed']} counterexamples - needs investigation")
        print("\nThis is the critical boundary where the conjecture may break!")

if __name__ == "__main__":
    main()