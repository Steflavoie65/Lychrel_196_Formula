#!/usr/bin/env python3
"""
Compare LaTeX formulas between the monolithic file and the split Documents.

Produces JSON report at results/formula_comparison_report.json and prints a short summary.
"""
import re
import json
from pathlib import Path


def read_file(p: Path):
    if not p.exists():
        return ''
    return p.read_text(encoding='utf-8', errors='ignore')


MONOLITH = Path(r'D:/Resolution_Lychrel/lychrel_correctif.tex')
DOCS = [
    Path(r'D:/Resolution_Lychrel/Documents/proof.tex'),
    Path(r'D:/Resolution_Lychrel/Documents/certificate.tex'),
    Path(r'D:/Resolution_Lychrel/Documents/supplementary.tex'),
]


math_patterns = [
    re.compile(r"\\begin\{equation\*?\}(.+?)\\end\{equation\*?\}", re.S),
    re.compile(r"\\begin\{align\*?\}(.+?)\\end\{align\*?\}", re.S),
    re.compile(r"\\\[(.+?)\\\]", re.S),
    re.compile(r"\$\$(.+?)\$\$", re.S),
    re.compile(r"\$(.+?)\$", re.S),
]


def extract_math(text: str):
    found = []
    for pat in math_patterns:
        for m in pat.findall(text):
            if isinstance(m, tuple):
                m = m[0]
            found.append(m)
    return found


def normalize(s: str):
    # Remove comments
    s = re.sub(r"%.*?$", "", s, flags=re.M)
    # Replace common wrappers
    s = re.sub(r"\\texttt\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\operatorname\{([^}]*)\}", r"\1", s)
    # Remove LaTeX spacing commands
    s = s.replace('\\,', ' ')
    s = s.replace('\\;', ' ')
    s = s.replace('\\:', ' ')
    # normalize whitespace
    s = re.sub(r"\s+", " ", s)
    s = s.strip()
    return s


def make_set(formulas):
    out = set()
    for f in formulas:
        nf = normalize(f)
        if nf:
            out.add(nf)
    return out


def fuzzy_present(fm, doc_set):
    # Try exact or substring match; also compare shortened prefix
    if fm in doc_set:
        return True
    short = fm[:120]
    for d in doc_set:
        if short in d:
            return True
    return False


def main():
    mon_text = read_file(MONOLITH)
    docs_text = '\n'.join(read_file(p) for p in DOCS)

    mon_math = extract_math(mon_text)
    doc_math = extract_math(docs_text)

    mon_set = make_set(mon_math)
    doc_set = make_set(doc_math)

    missing = []
    paraphrased = []
    for fm in sorted(mon_set):
        if fm in doc_set:
            continue
        elif fuzzy_present(fm, doc_set):
            paraphrased.append(fm)
        else:
            missing.append(fm)

    # Also check presence of key macros/labels
    keys = ['A^{(robust)}', 'A^{(ext)}', 'A^{(int)}', 'a_i + a_{d-1-i} + c_{i-1}', 'Jacobian', 'Hensel', '196']
    missing_keys = []
    for k in keys:
        if (k in mon_text) and (k not in docs_text):
            missing_keys.append(k)

    report = {
        'monolith_formula_count': len(mon_set),
        'docs_formula_count': len(doc_set),
        'n_missing': len(missing),
        'n_paraphrased': len(paraphrased),
        'missing_examples': missing[:200],
        'paraphrased_examples': paraphrased[:200],
        'missing_keys': missing_keys,
    }

    outdir = Path(r'D:/Resolution_Lychrel/results')
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / 'formula_comparison_report.json'
    outpath.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

    # Print short summary
    print(f"Monolith formulas: {report['monolith_formula_count']}")
    print(f"Docs formulas: {report['docs_formula_count']}")
    print(f"Missing formulas: {report['n_missing']}")
    print(f"Paraphrased (approx. matches): {report['n_paraphrased']}")
    if report['n_missing'] > 0:
        print('First missing example:')
        print(report['missing_examples'][0][:400])
    else:
        print('No missing formulas detected (modulo normalization).')


if __name__ == '__main__':
    main()
