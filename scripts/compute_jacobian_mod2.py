#!/usr/bin/env python3
"""Compute Jacobian rank modulo 2 for candidates using existing utilities.

This script reuses check_jacobian_mod2.analyze_n to compute the jacobian
rank for given integers. It can scan a directory of JSON files and try to
parse integer keys (or the top-level 'n' fields) to build a candidate list.

Outputs:
 - CSV summary at --output-csv (default: verifier/jacobian_summary.csv)
 - JSON summary at verifier/jacobian_summary.json

Usage examples:
 python verifier/compute_jacobian_mod2.py --numbers 196,121
 python verifier/compute_jacobian_mod2.py --input-dir ..\\Soumission_Pairs\\verifier --output-csv verifier/jacobian_summary.csv
"""

import argparse
import json
import os
import csv
from glob import glob

from check_jacobian_mod2 import analyze_n


def find_integers_in_json(path):
    """Try to extract integer keys or top-level integer fields from a JSON file.
    Returns a set of integers."""
    ints = set()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return ints
    # If data is dict, try keys
    if isinstance(data, dict):
        for k in data.keys():
            try:
                n = int(k)
                ints.add(n)
            except Exception:
                pass
        # try common fields
        for field in ('n', 'seed', 'candidate'):
            if field in data:
                try:
                    ints.add(int(data[field]))
                except Exception:
                    pass
    # If data is list, try entries with 'n' or integer items
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for field in ('n', 'seed', 'candidate'):
                    if field in item:
                        try:
                            ints.add(int(item[field]))
                        except Exception:
                            pass
            elif isinstance(item, int):
                ints.add(item)
            elif isinstance(item, str):
                try:
                    ints.add(int(item))
                except Exception:
                    pass
    return ints


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-dir', default=None,
                   help='Directory to scan for JSON certificates (optional)')
    p.add_argument('--numbers', default=None,
                   help='Comma-separated list of integers to analyze, e.g. 196,121')
    p.add_argument('--output-csv', default='verifier/jacobian_summary.csv',
                   help='CSV summary output')
    p.add_argument('--output-json', default='verifier/jacobian_summary.json',
                   help='JSON summary output')
    args = p.parse_args()

    numbers = set()
    if args.numbers:
        for tok in args.numbers.split(','):
            tok = tok.strip()
            if not tok:
                continue
            try:
                numbers.add(int(tok))
            except Exception:
                pass

    # scan input-dir for JSON and try to extract integers
    if args.input_dir:
        pattern = os.path.join(args.input_dir, '*.json')
        for path in glob(pattern):
            ints = find_integers_in_json(path)
            numbers.update(ints)

    # ensure at least 196 is analyzed if nothing else
    if not numbers:
        numbers.add(196)

    numbers = sorted(numbers)
    results = []
    for n in numbers:
        try:
            r = analyze_n(n)
            results.append(r)
        except Exception as e:
            results.append(dict(n=n, error=str(e)))

    # write CSV
    csv_fields = set()
    for row in results:
        csv_fields.update(row.keys())
    csv_fields = sorted(csv_fields)
    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
    with open(args.output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    # write JSON summary
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f'Wrote {len(results)} results to {args.output_csv} and {args.output_json}')


if __name__ == '__main__':
    main()
