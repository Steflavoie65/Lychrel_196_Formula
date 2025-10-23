#!/usr/bin/env python3
"""
generate_checksums.py
Génère les checksums SHA256 pour tous les fichiers de certificats

Usage:
    python generate_checksums.py

Output:
    checksums_manifest.txt
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime

def sha256_file(filepath):
    """Calculate SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):
            sha256.update(block)
    return sha256.hexdigest()

def generate_manifest():
    """Generate checksums for all certificate files"""

    verifier_dir = Path(__file__).parent

    # Files to checksum
    certificate_files = [
        'test_gap123.py',
        'test_extensions.py',
        '../test_3gaps_fast_20251020_174028.json',
        '../test_extensions_20251020_184255.json',
        '../validation_results_aext1.json',
        '../validation_results_aext2.json',
        '../validation_results_aext3.json',
        '../validation_results_aext4.json',
        '../validation_results_aext5.json',
        '../validation_results_class_III.json',
    ]

    manifest = []
    manifest.append("=" * 80)
    manifest.append("CHECKSUMS MANIFEST - Lychrel 196 Analysis")
    manifest.append(f"Generated: {datetime.now().isoformat()}")
    manifest.append("=" * 80)
    manifest.append("")

    for filepath in certificate_files:
        full_path = verifier_dir / filepath
        if full_path.exists():
            checksum = sha256_file(full_path)
            size = full_path.stat().st_size
            manifest.append(f"{checksum}  {filepath}  ({size} bytes)")
            print(f"✓ {filepath}: {checksum[:16]}...")
        else:
            manifest.append(f"MISSING  {filepath}")
            print(f"✗ {filepath}: FILE NOT FOUND")

    manifest.append("")
    manifest.append("=" * 80)
    manifest.append("Verification command:")
    manifest.append("  sha256sum -c checksums_manifest.txt")
    manifest.append("=" * 80)

    # Write manifest
    manifest_path = verifier_dir / 'checksums_manifest.txt'
    with open(manifest_path, 'w') as f:
        f.write('\n'.join(manifest))

    print(f"\n✅ Manifest saved to: {manifest_path}")
    return manifest_path

if __name__ == "__main__":
    generate_manifest()