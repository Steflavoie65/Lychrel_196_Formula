#!/usr/bin/env python3
"""
Validation de la croissance de l'invariant Φ sur l'orbite de 196
"""

def valuation_2(n):
    """Calcule la valuation 2-adique de n"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def compute_A_robust(n):
    """Calcule l'asymétrie robuste A_robust(n)"""
    digits = list(map(int, str(n)))
    d = len(digits)
    
    # Asymétrie externe
    a_ext = max(0, abs(digits[0] - digits[-1]) - 1)
    
    # Asymétrie interne
    a_int = 0
    for i in range(1, (d-1)//2 + 1):
        diff = abs(digits[i] - digits[d-1-i])
        a_int += max(0, diff - 1)
    
    # Asymétrie des retenues (approximation basée sur la parité)
    a_carry = 1 if (n + int(str(n)[::-1])) % 2 != 0 else 0
    
    return a_ext + a_int + a_carry

def compute_phi(n, alpha=0.5):
    """Calcule l'invariant de persistance Φ(n)"""
    rev_n = int(str(n)[::-1])
    v2 = valuation_2(n - rev_n)
    A_robust = compute_A_robust(n)
    return v2 + alpha * A_robust

def reverse_add(n):
    """Applique T(n) = n + reverse(n)"""
    return n + int(str(n)[::-1])

def validate_phi_growth(start=196, max_iter=10000, alpha=0.5):
    """Valide la croissance de Φ sur l'orbite complète"""
    current = start
    phi_values = []
    violations = []
    
    phi_prev = compute_phi(current, alpha)
    phi_values.append(phi_prev)
    
    print(f"Validation de la croissance de Φ sur {max_iter} itérations")
    print(f"Paramètre α = {alpha}")
    print("=" * 60)
    print(f"Itération 0: n = {current}, Φ = {phi_prev:.6f}")
    
    for i in range(1, max_iter + 1):
        current = reverse_add(current)
        phi_current = compute_phi(current, alpha)
        phi_values.append(phi_current)
        
        delta = phi_current - phi_prev
        
        if i % 1000 == 0:
            digits = len(str(current))
            print(f"Itération {i}: n ({digits} chiffres), Φ = {phi_current:.6f}, Δ = {delta:.6f}")
        
        # Détection des violations
        if delta < -1e-10:
            violations.append((i, phi_prev, phi_current, delta))
            print(f"⚠️  Violation à l'itération {i}: Δ = {delta:.6f}")
        
        phi_prev = phi_current
    
    # Analyse des résultats
    print("\n" + "=" * 60)
    print("ANALYSE FINALE")
    print("=" * 60)
    
    if not violations:
        print("✅ AUCUNE violation de la croissance détectée!")
        
        # Statistiques
        deltas = [phi_values[i+1] - phi_values[i] for i in range(len(phi_values)-1)]
        stats = {
            'delta_moyen': sum(deltas) / len(deltas),
            'delta_min': min(deltas),
            'delta_max': max(deltas),
            'croissance_totale': phi_values[-1] - phi_values[0],
            'phi_final': phi_values[-1]
        }
        
        print(f"📈 Croissance totale: {stats['croissance_totale']:.6f}")
        print(f"📊 Delta moyen: {stats['delta_moyen']:.6f}")
        print(f"📉 Delta minimum: {stats['delta_min']:.6f}")
        print(f"📈 Delta maximum: {stats['delta_max']:.6f}")
        print(f"🎯 Φ final: {stats['phi_final']:.6f}")
        
    else:
        print(f"❌ {len(violations)} violations détectées:")
        for i, phi_prev, phi_current, delta in violations[:5]:  # Affiche les 5 premières
            print(f"   Itération {i}: Φ = {phi_prev:.6f} → {phi_current:.6f}, Δ = {delta:.6f}")
    
    return violations, phi_values

if __name__ == "__main__":
    violations, phi_values = validate_phi_growth()
    
    if not violations:
        print("\n🎉 VALIDATION RÉUSSIE!")
        print("L'invariant Φ montre une croissance monotone sur 10,000 itérations.")
        print("Cela confirme l'obstruction structurelle à la formation de palindromes.")
    else:
        print("\n💥 VALIDATION ÉCHOUÉE!")
        print("Des violations de croissance ont été détectées.")