#!/usr/bin/env python3
"""
Update results/manifest_sha256.json by adding SHA-256 entries for JSON files
located in the certificates/ directory and for results/validation_results_aext9.json
if they are missing.
"""
import json
import hashlib
from pathlib import Path

REPO = Path('d:/Resolution_Lychrel')
MANIFEST = REPO / 'results' / 'manifest_sha256.json'
CERT_DIR = REPO / 'certificates'
EXTRA_FILES = [REPO / 'results' / 'validation_results_aext9.json']

# Gather candidate files from certificates dir (json files)
cert_files = sorted(CERT_DIR.glob('*.json'))
candidates = EXTRA_FILES + cert_files

# Load existing manifest
with open(MANIFEST, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

existing = {entry['path'].replace('\\','/'): entry['sha256'] for entry in manifest.get('entries', [])}

added = []
for p in candidates:
    rel = p.relative_to(REPO).as_posix()
    if rel in existing:
        # already present
        continue
    if not p.exists():
        print(f"Skipping missing file: {rel}")
        continue
    # compute sha256
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    digest = h.hexdigest()
    manifest['entries'].append({'path': rel.replace('/','\\'), 'sha256': digest})
    added.append((rel, digest))

# Optionally sort entries by path
manifest['entries'] = sorted(manifest['entries'], key=lambda e: e['path'])

# Write back manifest (overwrite)
with open(MANIFEST, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"Updated manifest: {MANIFEST}")
if added:
    print('\nAdded entries:')
    for rel,d in added:
        print(f"  {rel} -> {d}")
else:
    print('\nNo new entries added.')
