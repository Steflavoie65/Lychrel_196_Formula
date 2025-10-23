#!/usr/bin/env python3
"""
Script de vérification d'intégrité pour la soumission aux pairs.
Calcule les sommes de contrôle SHA256 de tous les fichiers importants.
"""

import hashlib
import os
import json
from pathlib import Path

def calculate_sha256(file_path):
    """Calcule le SHA256 d'un fichier."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def main():
    """Vérifie l'intégrité de tous les fichiers de soumission."""
    base_dir = Path(__file__).parent

    # Fichiers à vérifier avec leurs SHA256 attendus (d'après annex_repro.tex)
    expected_hashes = {
        "validation_results_aext5.json": "37EF75F6339257782E72AB9A9BA7484929A19F842D006B570FEB200EFD327F78",
        "verifier/verify_196_mod2.py": "3c2f161e243a52c0421b02ec891741dc8bf5bd23a9cf0fc08f7ea5fc3de6ab94",
        "verifier/check_jacobian_mod2.py": "3cfe652b2e9d919ec6984dc683fde49816117c3368291f6e395e2204c18c00cc",
        "verifier/hensel_lift_results.json": "8e4e1adc91e43bf04349e4a13dff186bda8ef5dbf19da36225ea170f6defe417",
        "K8_portes.json": "be214fdedc41b8f1cc711411cc16ebcdc6d9d9636ef2a003c6c22de7d27d2b40"
    }

    print("Vérification d'intégrité des fichiers de soumission")
    print("=" * 60)

    results = {}
    all_good = True

    # Vérifier tous les fichiers présents
    for file_path in base_dir.glob("*"):
        if file_path.is_file() and file_path.name != "verify_integrity.py" and file_path.name != "README.md":
            actual_hash = calculate_sha256(file_path).upper()
            results[file_path.name] = actual_hash

            # Vérifier si on a un hash attendu
            expected = expected_hashes.get(file_path.name)
            if expected:
                if actual_hash == expected:
                    status = "✓ CORRECT"
                else:
                    status = f"✗ INCORRECT (attendu: {expected})"
                    all_good = False
            else:
                status = "? NON VÉRIFIÉ"

            print(f"{file_path.name:<35} {actual_hash} {status}")

    print("\n" + "=" * 60)
    if all_good:
        print("✓ Tous les fichiers vérifiés sont intègres !")
    else:
        print("✗ Certains fichiers ne correspondent pas aux sommes de contrôle attendues.")

    # Sauvegarder les résultats
    with open(base_dir / "integrity_check.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Résultats sauvegardés dans integrity_check.json")

if __name__ == "__main__":
    main()