# Certificat — orbit modulo 4096

Résumé de l'exécution de `scripts/check_orbit_moduli.py` pour M = 4096 (2^12).

- orbit_size_mod_M: 58
- cycle_start_index: 16
- checked_representatives: 58
- theoretical_by_hensel_count: 58
- needs_further_check_count: 0

Interprétation :

Les 58 représentants rencontrés ont été vérifiés de la même manière que pour M = 1024 : obstruction mod 2 + rang du Jacobien modulo 2. Tous les représentants ont été classés `theoretical_by_hensel`.

Fichiers associés :

- `results/orbit_moduli_summary.json` (entrée pour 4096)
- `scripts/check_orbit_moduli.py`

Pour obtenir la liste des représentants concrets :

```powershell
python .\scripts\check_orbit_moduli.py --dump-representatives --mod 4096 --max-iter 20000
```
