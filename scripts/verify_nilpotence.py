#!/usr/bin/env python3
"""
Preuve de (I+R)² ≡ 0 (mod 2) pour la matrice de renversement R
"""

import numpy as np

def create_reversal_matrix(d):
    """Crée la matrice de renversement R de taille d x d"""
    R = np.zeros((d, d), dtype=int)
    for i in range(d):
        R[i, d-1-i] = 1
    return R

def verify_nilpotence_mod2(d_max=100):
    """Vérifie que (I+R)² ≡ 0 (mod 2) pour toutes tailles de 1 à d_max"""
    print("Vérification de (I+R)² ≡ 0 (mod 2)")
    print("=" * 50)
    
    for d in range(1, d_max + 1):
        I = np.eye(d, dtype=int)
        R = create_reversal_matrix(d)
        J = I + R
        J_squared = np.matmul(J, J)
        
        # Vérification modulo 2
        J_squared_mod2 = J_squared % 2
        is_nilpotent = np.all(J_squared_mod2 == 0)
        
        print(f"Taille d = {d:3d}: (I+R)² ≡ 0 (mod 2) ? {is_nilpotent}")
        
        if not is_nilpotent:
            print(f"❌ Échec pour d = {d}")
            print("Matrice (I+R)² mod 2:")
            print(J_squared_mod2)
            return False
    
    print(f"\n✅ Vérification réussie pour d = 1 à {d_max}!")
    return True

def theoretical_proof():
    """Preuve théorique de la nilpotence modulo 2"""
    print("\n" + "=" * 60)
    print("PREUVE THÉORIQUE")
    print("=" * 60)
    print("Soit R la matrice de renversement : R_{i,j} = 1 si j = d+1-i, 0 sinon")
    print("Propriétés :")
    print("1. R² = I (car renverser deux fois donne l'identité)")
    print("2. (I + R)² = I + 2R + R² = I + 2R + I = 2I + 2R = 2(I + R)")
    print("3. Donc (I + R)² = 2(I + R)")
    print("4. Modulo 2 : (I + R)² ≡ 0 (mod 2)")
    print("5. Ainsi, J = I + R est nilpotente modulo 2")
    print("\n✅ Preuve théorique complète!")

if __name__ == "__main__":
    # Vérification computationnelle
    verify_nilpotence_mod2(20)
    
    # Preuve théorique
    theoretical_proof()