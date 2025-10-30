#!/usr/bin/env python3
"""
Verify presence of expected certificate files and compare SHA-256 checksums
using results/manifest_sha256.json.

Run from repository root or anywhere; paths in manifest are relative to repo root.
"""
import json
import hashlib
import os
from pathlib import Path

REPO_ROOT = Path("d:/Resolution_Lychrel")
MANIFEST = REPO_ROOT / "results" / "manifest_sha256.json"

# Files we expect according to the updated certificate.tex mapping
EXPECTED = [
    REPO_ROOT / "results" / "trajectory_obstruction_log.json",
    REPO_ROOT / "results" / "orbit_moduli_summary.json",
    REPO_ROOT / "results" / "test_extensions_mod5.json",
    REPO_ROOT / "results" / "validation_results_aext9.json",
    REPO_ROOT / "certificates" / "validation_results_aext1.json",
    REPO_ROOT / "certificates" / "validation_results_aext2.json",
    REPO_ROOT / "certificates" / "validation_results_aext3.json",
    REPO_ROOT / "certificates" / "validation_results_aext4.json",
    REPO_ROOT / "certificates" / "validation_results_aext5.json",
    REPO_ROOT / "certificates" / "combined_certificates_196.json",
    REPO_ROOT / "certificates" / "test_3gaps_enhanced_20251021_154322.json",
    REPO_ROOT / "certificates" / "test_3gaps_enhanced_20251022_151510.json",
    REPO_ROOT / "certificates" / "test_3gaps_enhanced_20251023_073903.json",
    REPO_ROOT / "certificates" / "test_3gaps_enhanced_20251023_074034.json",
    REPO_ROOT / "results" / "prove_d3_persistence.json",
]

# Load manifest
with open(MANIFEST, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

manifest_map = {entry['path'].replace('\\','/'): entry['sha256'] for entry in manifest.get('entries', [])}

print("Verification report for expected certificate files:\n")
missing = []
checksum_mismatch = []
ok = []

for p in EXPECTED:
    rel = p.relative_to(REPO_ROOT).as_posix()
    exists = p.exists()
    if not exists:
        print(f"MISSING: {rel}")
        missing.append(rel)
        continue

    # compute sha256 of file bytes
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    digest = h.hexdigest()

    # check manifest
    if rel in manifest_map:
        expected = manifest_map[rel]
        if digest.lower() == expected.lower():
            print(f"OK: {rel}  (checksum matches)")
            ok.append(rel)
        else:
            print(f"CHECKSUM MISMATCH: {rel}\n  expected: {expected}\n  found:    {digest}")
            checksum_mismatch.append((rel, expected, digest))
    else:
        print(f"NO MANIFEST ENTRY: {rel}  (found file; no checksum to compare)")
        ok.append(rel)

print('\nSummary:')
print(f"  present & checksum OK: {len(ok)}")
print(f"  missing: {len(missing)}")
print(f"  checksum mismatches: {len(checksum_mismatch)}")

if missing or checksum_mismatch:
    exit(2)
else:
    exit(0)
