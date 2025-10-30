import re
from collections import defaultdict

INPUT_FILE = r"../lychrel_correctif.tex"
OUTPUT_FILE = r"../lychrel_correctif_fixed.tex"

# Expressions régulières pour labels et références
LABEL_PATTERN = re.compile(r'(\\label\{([^}]+)\})')
REF_PATTERN = re.compile(r'(\\(ref|eqref|pageref)\{([^}]+)\})')

# Lire le fichier
with open(INPUT_FILE, encoding='utf-8') as f:
    lines = f.readlines()

label_count = defaultdict(int)
label_map = defaultdict(list)

# Première passe : recenser tous les labels
for i, line in enumerate(lines):
    for match in LABEL_PATTERN.finditer(line):
        label = match.group(2)
        label_count[label] += 1
        label_map[label].append(i)

# Générer les nouveaux noms de labels
new_label_names = {}
for label, occurrences in label_map.items():
    if label_count[label] > 1:
        for idx, line_num in enumerate(occurrences, 1):
            new_label = f"{label}_{idx}"
            new_label_names[(label, line_num)] = new_label
    else:
        new_label_names[(label, occurrences[0])] = label

# Deuxième passe : remplacer labels et références
fixed_lines = []
for i, line in enumerate(lines):
    # Remplacer les labels
    def label_replacer(m):
        label = m.group(2)
        key = (label, i)
        return f"\\label{{{new_label_names.get(key, label)}}}"
    line = LABEL_PATTERN.sub(label_replacer, line)

    # Remplacer les références
    def ref_replacer(m):
        ref_type = m.group(2)
        label = m.group(3)
        # Cherche le bon label pour cette ligne
        # Si label dupliqué, on prend le plus proche précédent
        candidates = [(k, v) for (k, v) in new_label_names.items() if k[0] == label]
        if len(candidates) == 1:
            new_label = candidates[0][1]
        elif len(candidates) > 1:
            # Cherche la plus proche
            prev = [v for (k, v) in candidates if k[1] <= i]
            new_label = prev[-1] if prev else candidates[0][1]
        else:
            new_label = label
        return f"\\{ref_type}{{{new_label}}}"
    line = REF_PATTERN.sub(ref_replacer, line)
    fixed_lines.append(line)

# Écrire le nouveau fichier
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"Correction terminée. Fichier généré : {OUTPUT_FILE}")
