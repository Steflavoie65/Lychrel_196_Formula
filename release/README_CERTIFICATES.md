# Archive: certificates_for_review.zip

Contenu :

- `certificates/orbit_moduli_1024.md`
- `certificates/orbit_moduli_4096.md`
- `certificates/orbit_moduli_1000000.md`
- `results/orbit_moduli_summary.json`
- `CERTIFICATES_FOR_REVIEWER.md` (section mise à jour pour inclure ces éléments)

Usage :

1. Extraire l'archive.
2. Vérifier que les checksums dans `manifests/` correspondent aux fichiers (si nécessaire).
3. Pour reproduire les représentants détaillés, exécuter :

```powershell
python .\scripts\check_orbit_moduli.py --dump-representatives --mod <M> --max-iter 20000
```
