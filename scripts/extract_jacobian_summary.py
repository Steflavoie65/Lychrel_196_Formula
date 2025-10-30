import json
from collections import Counter, defaultdict

infile = r"results\trajectory_obstruction_log.json"
out_json = r"results\jacobian_summary_extracted.json"
out_tex = r"results\jacobian_summary.tex"

with open(infile, 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data.get('results', [])
N = len(results)
count_obstruction = 0
count_full_rank = 0
count_both = 0
constraints_counter = Counter()
rank_counter = Counter()

for entry in results:
    if entry.get('obstruction_mod2'):
        count_obstruction += 1
    if entry.get('jacobian_full_row_rank'):
        count_full_rank += 1
    if entry.get('obstruction_mod2') and entry.get('jacobian_full_row_rank'):
        count_both += 1
    constraints_counter[entry.get('jacobian_constraints', 0)] += 1
    rank_counter[entry.get('jacobian_rank_mod2', 0)] += 1

summary = {
    'total_entries': N,
    'obstruction_mod2_count': count_obstruction,
    'jacobian_full_row_rank_count': count_full_rank,
    'both_obstruction_and_fullrank': count_both,
    'constraints_distribution': dict(constraints_counter),
    'rank_distribution': dict(rank_counter)
}

with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

# Generate a small LaTeX table
lines = []
lines.append('% Auto-generated Jacobian summary table')
lines.append('\\begin{table}[ht]')
lines.append('\\centering')
lines.append('\\begin{tabular}{lrr}')
lines.append('\\hline')
lines.append('Metric & Count & Fraction \\')
lines.append('\\hline')
lines.append(f'Total iterations & {N} & 1.00 \\')
lines.append(f'Obstruction mod 2 & {count_obstruction} & {count_obstruction/N:.4f} \\')
lines.append(f'Jacobian full row rank (mod 2) & {count_full_rank} & {count_full_rank/N:.4f} \\')
lines.append(f'Both obstruction and full rank & {count_both} & {count_both/N:.4f} \\')
lines.append('\\hline')
lines.append('\\end{tabular}')
lines.append('\\caption{Résumé des analyses Jacobiennes pour la trajectoire de 196 (0..9999).}')
lines.append('\\label{tab:jacobian_summary}')
lines.append('\\end{table}')

with open(out_tex, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('Wrote', out_json, 'and', out_tex)
print(json.dumps(summary, indent=2))
