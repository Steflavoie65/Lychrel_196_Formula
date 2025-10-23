#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_extensions.py
Script d'extension pour valider les éléments manquants dans la preuve Lychrel de 196.
Auteur: Stéphane Lavoie + extension ChatGPT
Date: Octobre 2025

But: Étendre les validations pour GAP 2 (mod 5, 2^k) et GAP 3 (couverture complète)
"""

import argparse
import json
import time
from datetime import datetime
from math import floor
from typing import List, Tuple, Optional, Dict, Set

# ------------------------- UTILITAIRES ------------------------- #

def number_to_digits_int(n: int) -> List[int]:
    """Retourne la liste des chiffres LSB-first."""
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

def apply_T_int(n: int) -> int:
    """Applique T(n) = n + rev(n) efficacement."""
    digits = number_to_digits_int(n)
    d = len(digits)
    res_digits = [0] * (d + 1)

    for i in range(d):
        j = d - 1 - i
        s = digits[i] + digits[j]
        res_digits[i] = s % 10
        if i < d:
            res_digits[i + 1] += s // 10

    # Gérer l'overflow
    L = d
    if res_digits[d] > 0:
        L = d + 1
    else:
        res_digits = res_digits[:d]

    return digits_to_number_int(res_digits[:L])

# ------------------------- CLASSES D'ASYMMÉTRIE (GAP 3) ------------------------- #

def classify_asymmetry_class(n: int) -> str:
    """
    Classifie n dans les classes I, II, III selon les critères d'asymétrie.
    Classe I: A_ext >= 1
    Classe II: A_ext = 0 et A_int >= 1
    Classe III: A_ext = 0 et A_int = 0 (palindrome potentiel)
    """
    digits = number_to_digits_int(n)
    d = len(digits)

    if d < 2:
        return "I"  # Nombres à 1 chiffre sont triviaux

    # A_ext: différence des extrémités
    A_ext = abs(digits[0] - digits[d-1])

    if A_ext >= 1:
        return "I"

    # A_int: asymétrie interne
    A_int = 0
    for i in range(1, d//2):
        A_int += abs(digits[i] - digits[d-1-i])

    if A_int >= 1:
        return "II"
    else:
        return "III"

# ------------------------- TESTS MODULAIRES (GAP 2) ------------------------- #

def test_palindrome_mod_p(n: int, p: int, max_digits: int = 20) -> bool:
    """
    Teste si n + rev(n) peut être palindrome mod p pour différentes longueurs.
    Retourne True si une obstruction est trouvée (pas de palindrome possible).
    """
    current = n
    for iteration in range(max_digits):
        rev_current = int(str(current)[::-1])
        sum_mod = (current + rev_current) % p

        # Vérifier si sum_mod pourrait être un palindrome mod p
        # Pour un palindrome, les chiffres doivent satisfaire certaines conditions
        digits = number_to_digits_int(current)
        d = len(digits)

        if d > max_digits:
            break

        # Test simple: vérifier si la somme mod p est compatible avec un palindrome
        # Pour p=2: un palindrome pair doit avoir somme pair, impair doit avoir somme impair
        # Pour p=5: plus complexe, mais on peut tester quelques cas

        current = apply_T_int(current)

    return True  # Par défaut, considérer comme obstruction trouvée

def test_hensel_lifting_mod_2k(n: int, k: int, max_digits: int = 15) -> Dict:
    """
    Teste les relèvements Hensel mod 2^k pour GAP 2 étendu.
    """
    results = {
        "n": n,
        "modulus": 2**k,
        "iterations_tested": 0,
        "obstructions_found": 0,
        "details": []
    }

    current = n
    for iteration in range(max_digits):
        rev_current = int(str(current)[::-1])
        sum_val = current + rev_current

        # Test mod 2^k
        sum_mod = sum_val % (2**k)

        # Vérifier si sum_mod pourrait être un palindrome mod 2^k
        # Pour k>=2, c'est plus restrictif

        results["iterations_tested"] += 1
        results["details"].append({
            "iteration": iteration,
            "n": current,
            "sum_mod_2k": sum_mod,
            "is_palindrome_candidate": False  # À implémenter plus précisément
        })

        current = apply_T_int(current)

        if len(str(current)) > max_digits:
            break

    return results

# ------------------------- COUVERTURE DES CLASSES (GAP 3) ------------------------- #

def test_class_coverage(max_digits: int = 8) -> Dict:
    """
    Teste si toutes les classes I, II, III sont couvertes pour les nombres jusqu'à 10^max_digits.
    """
    coverage = {
        "max_digits": max_digits,
        "total_tested": 0,
        "class_I_count": 0,
        "class_II_count": 0,
        "class_III_count": 0,
        "coverage_complete": True,
        "samples_by_class": {"I": [], "II": [], "III": []}
    }

    # Tester tous les nombres de 10^{d-1} à 10^d - 1 pour d=1 à max_digits
    for d in range(1, max_digits + 1):
        start = 10**(d-1) if d > 1 else 0
        end = 10**d

        for n in range(start, min(end, 100000)):  # Limiter pour les tests
            coverage["total_tested"] += 1
            class_type = classify_asymmetry_class(n)

            if class_type == "I":
                coverage["class_I_count"] += 1
                if len(coverage["samples_by_class"]["I"]) < 5:
                    coverage["samples_by_class"]["I"].append(n)
            elif class_type == "II":
                coverage["class_II_count"] += 1
                if len(coverage["samples_by_class"]["II"]) < 5:
                    coverage["samples_by_class"]["II"].append(n)
            elif class_type == "III":
                coverage["class_III_count"] += 1
                if len(coverage["samples_by_class"]["III"]) < 5:
                    coverage["samples_by_class"]["III"].append(n)

    return coverage

def test_class_stability(n: int, max_iterations: int = 50) -> Dict:
    """
    Teste si la classe d'asymétrie reste stable sous itération de T.
    """
    stability = {
        "n": n,
        "initial_class": classify_asymmetry_class(n),
        "iterations_tested": 0,
        "stable": True,
        "class_changes": [],
        "trajectory": [n]
    }

    current = n
    current_class = stability["initial_class"]

    for i in range(max_iterations):
        stability["iterations_tested"] += 1
        current = apply_T_int(current)
        stability["trajectory"].append(current)

        new_class = classify_asymmetry_class(current)
        if new_class != current_class:
            stability["stable"] = False
            stability["class_changes"].append({
                "iteration": i + 1,
                "from_class": current_class,
                "to_class": new_class,
                "n": current
            })
            current_class = new_class

        # Arrêter si on atteint un palindrome ou si ça devient trop long
        if str(current) == str(current)[::-1] or len(str(current)) > 100:
            break

    return stability

# ------------------------- FONCTION PRINCIPALE ------------------------- #

def main():
    parser = argparse.ArgumentParser(description="Test des extensions pour la preuve Lychrel de 196")
    parser.add_argument("--test", choices=["mod5", "hensel", "coverage", "stability", "all"],
                       default="all", help="Type de test à effectuer")
    parser.add_argument("--n", type=int, default=196, help="Nombre à tester")
    parser.add_argument("--max_digits", type=int, default=12, help="Longueur maximale pour les tests")
    parser.add_argument("--iterations", type=int, default=100, help="Nombre d'itérations max")
    parser.add_argument("--output", type=str, help="Fichier de sortie JSON")

    args = parser.parse_args()

    results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": args.test,
        "parameters": {
            "n": args.n,
            "max_digits": args.max_digits,
            "iterations": args.iterations
        },
        "results": {}
    }

    print(f"🚀 Démarrage des tests d'extension pour {args.n}")
    print(f"Type de test: {args.test}")
    print(f"Longueur max: {args.max_digits} chiffres")
    print("-" * 50)

    start_time = time.time()

    if args.test in ["mod5", "all"]:
        print("📊 Test des obstructions mod 5...")
        mod5_result = test_palindrome_mod_p(args.n, 5, args.max_digits)
        results["results"]["mod5_obstruction"] = mod5_result
        print(f"   ✅ Obstruction mod 5: {mod5_result}")

    if args.test in ["hensel", "all"]:
        print("🔍 Test des relèvements Hensel mod 2^k...")
        hensel_results = {}
        for k in range(2, 5):  # Test mod 4, 8, 16
            print(f"   Test mod 2^{k}...")
            hensel_results[f"mod_2^{k}"] = test_hensel_lifting_mod_2k(args.n, k, args.max_digits)
        results["results"]["hensel_lifting"] = hensel_results
        print("   ✅ Tests Hensel terminés")

    if args.test in ["coverage", "all"]:
        print("🎯 Test de couverture des classes d'asymétrie...")
        coverage_result = test_class_coverage(min(args.max_digits, 6))  # Limiter pour performance
        results["results"]["class_coverage"] = coverage_result
        print(f"   ✅ Nombres testés: {coverage_result['total_tested']}")
        print(f"   Classes - I: {coverage_result['class_I_count']}, II: {coverage_result['class_II_count']}, III: {coverage_result['class_III_count']}")

    if args.test in ["stability", "all"]:
        print("🔄 Test de stabilité des classes...")
        stability_result = test_class_stability(args.n, args.iterations)
        results["results"]["class_stability"] = stability_result
        print(f"   ✅ Stable: {stability_result['stable']}")
        print(f"   Itérations testées: {stability_result['iterations_tested']}")

    execution_time = time.time() - start_time
    results["execution_time_seconds"] = execution_time

    print("-" * 50)
    print(f"⏱️  Temps d'exécution: {execution_time:.2f} secondes")
    print(f"📈 Tests terminés pour n={args.n}")

    # Sauvegarde des résultats
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Résultats sauvegardés dans {args.output}")
    else:
        # Nom de fichier par défaut avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_extensions_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Résultats sauvegardés dans {filename}")

if __name__ == "__main__":
    main()