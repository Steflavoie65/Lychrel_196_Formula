# Certificat — orbit modulo 1_000_000

Résumé de l'exécution de `scripts/check_orbit_moduli.py` pour M = 1_000_000.

- orbit_size_mod_M: 1098
- cycle_start_index: 452
- checked_representatives: 1098
- theoretical_by_hensel_count: 1098
- needs_further_check_count: 0

Interprétation :

Pour le module 10^6 nous avons observé 1098 résidus distincts atteints avant répétition ; pour chacun, un représentant concret a été vérifié et a donné `theoretical_by_hensel`.

Remarque pratique : la vérification de 1098 représentants a pris sensiblement plus de temps que pour les modules 1024/4096, mais elle reste totalement réalisée et inscrite dans `results/orbit_moduli_summary.json`.

Fichiers associés :

- `results/orbit_moduli_summary.json` (entrée pour 1000000)
- `scripts/check_orbit_moduli.py`

Pour dumper les représentants :

```powershell
python .\scripts\check_orbit_moduli.py --dump-representatives --mod 1000000 --max-iter 20000
```
