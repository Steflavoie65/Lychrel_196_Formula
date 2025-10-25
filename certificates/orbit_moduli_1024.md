# Certificat — orbit modulo 1024

Résumé de l'exécution de `scripts/check_orbit_moduli.py` pour M = 1024 (2^10).

- orbit_size_mod_M: 52
- cycle_start_index: 7
- checked_representatives: 52
- theoretical_by_hensel_count: 52
- needs_further_check_count: 0

Interprétation :

Chaque classe de résidu modulo 1024 rencontrée par la trajectoire T^j(196) (j parcouru) a été représentée par un entier concret rencontré durant l'exécution. Pour chacun de ces représentants, les vérifications suivantes ont été faites :

- test d'obstruction modulo 2 (aucune solution mod 2),
- construction du Jacobien linéarisé et calcul du rang modulo 2,
- conclusion Hensel (lorsque le Jacobien est non-dégénéré, conclusion "theoretical_by_hensel").

Tous les 52 représentants vérifiés ont abouti à `theoretical_by_hensel`.

Fichiers associés :

- `results/orbit_moduli_summary.json` (entrée pour 1024)
- `scripts/check_orbit_moduli.py` (script ayant produit ces certificats)

Pour extraire les représentants concrets rencontrés (liste), exécuter :

```powershell
python .\scripts\check_orbit_moduli.py --dump-representatives --mod 1024 --max-iter 20000
```

Remarque : la preuve mathématique qui convertit la vérification d'un représentant en couverture de la classe modulo M est donnée dans le manuscrit (`lychrel_correctif.tex`) sous la forme d'un lemme Hensel/invariance; vérifiez l'énoncé correspondant et référez les labels `thm:196_hensel-*` mentionnés dans le texte.
