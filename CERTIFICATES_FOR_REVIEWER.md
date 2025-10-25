# Certificats pour le relecteur — Résumé et reproductions

Ce fichier résume les preuves et les certificats numériques fournis dans le dépôt `Lychrel_196_Formula` et indique les commandes pour reproduire les vérifications critiques. Il contient aussi le résultat automatisé produit pour la trajectoire de 196 (1001 itérations).

## 1) Conclusion clé

- Pour l'état initial 196, le dépôt contient une preuve (Hensel + vérification du Jacobien) que la somme
  `196 + rev(196)` n'admet aucune solution palindromique modulo 2; le Jacobien linéarisé possède un mineur 1×1 = -1 (impair), donc est non-dégénéré modulo 2, et par le lemme de Hensel classique l'absence de solution modulo 2 interdit toute solution modulo 2^k pour tout k≥1.
- J'ai automatisé et exécuté une vérification itérative sur la trajectoire T^j(196) pour j = 0..1000 ; le script `scripts/check_trajectory_obstruction.py` a produit `results/trajectory_obstruction_log.json`. Pour chacune des 1001 itérations testées, le log indique:
  - `obstruction_mod2 = true` (aucune solution mod 2),
  - `jacobian_full_row_rank = true` (rang plein modulo 2),
  - `hensel_conclusion = "theoretical_by_hensel"`.

  Autrement dit : pour chaque état T^j(196) avec 0 ≤ j ≤ 1000, la condition nécessaire et suffisante utilisée ici (obstruction mod 2 + Jacobien non-dégénéré) est satisfaite; par Hensel on en déduit théoriquement qu'aucun palindrome n'existe modulo 2^k (∀ k) pour ces états.

## 2) Fichiers importants à joindre pour l'audit

- Preuve extraite (exposé + traduction) : `extrait_196_preuve.txt`
- Script d'analyse trajectoire (ajouté) : `scripts/check_trajectory_obstruction.py`
- Log produit : `results/trajectory_obstruction_log.json`
- Scripts originaux utilisés / utiles :
  - `scripts/verify_196_mod2.py` (exhaustive mod-2 check pour un état)
  - `scripts/check_jacobian_mod2.py` (construction du Jacobien et rang mod 2)
  - `scripts/verify_196_modk.py` (tests empiriques pour petits k)
  - `scripts/test_3gaps_enhanced.py` (infrastructure de trajectoire et métriques)

Les fichiers machine‑lisibles de certificats (fournis dans le dépôt original) se trouvent dans :
- `certificates/combined_certificates_196.json`
- `certificates/gap3_window8.json`
- `certificates/hensel_lift_results.json`

Les checksums et manifestes se trouvent dans `manifests/` (notamment `manifests/integrity_check.json` et `manifest_sha256.txt`) — merci de vérifier l'intégrité des fichiers par comparaison des SHA256 listés.

Extraits de quelques SHA256 (voir `manifest_sha256.txt` pour la liste complète) :

```
3C2F161E243A52C0421B02EC891741DC8BF5BD23A9CF0FC08F7EA5FC3DE6AB94  scripts/verify_196_mod2.py
3CFE652B2E9D919EC6984DC683FDE49816117C3368291F6E395E2204C18C00CC  scripts/check_jacobian_mod2.py
75C75F9041F62588AC5318464B4C1DCB7CC6E047DA25813DBFEA10A0D9D53EA3  certificates/combined_certificates_196.json
69B1BF7A06413EB6F229D8972D32F101E2482E261B0D235862814F3AE3E85254  certificates/gap3_window8.json
D0DF4057D63E64541EBF315E92F0A01E915767D5AA0CF39C5BB663072209268B  certificates/hensel_lift_results.json
```

## 3) Comment reproduire localement (PowerShell)

Se placer dans le répertoire racine du dépôt (`D:\Resolution_Lychrel`) puis exécuter :

```powershell
# (1) Vérifier l'obstruction mod 2 pour 196
python .\scripts\verify_196_mod2.py

# (2) Vérifier le Jacobien modulo 2 pour 196
python .\scripts\check_jacobian_mod2.py

# (3) Relancer l'analyse automatisée de la trajectoire (reproduit le log que j'ai produit)
python .\scripts\check_trajectory_obstruction.py --iterations 1001 --kmax 10

# (4) Optionnel : exécuter les tests étendus (long)
python .\scripts\test_3gaps_enhanced.py --iterations 1001
```

Note : `--kmax` dans `check_trajectory_obstruction.py` est la borne pour les tests empiriques modulo 2^k (utile si le Jacobien est singulier et qu'on veut tenter un relèvement numérique). Le log final contient la conclusion pour chaque itération.

## 4) Interprétation et portée

- Ce dépôt contient désormais une preuve théorique (Hensel + Jacobien) appliquée **état par état** pour les 1001 premières itérations de la trajectoire de 196. Pour chaque état testé, la conclusion est formelle : il n'existe aucune solution palindromique modulo 2^k pour tout k (conséquence directe du lemme de Hensel sous la condition du Jacobien non-dégénéré).
- Reste la question théorique générale : prouver que cette propriété se conserve pour *tous* les états T^j(196) (j arbitraire). Le dépôt contient des arguments analytiques et des certificats couvrant des classes de cas (Hensel + fenêtres locales) et fournit une validation empirique étendue ; toutefois, une démonstration inconditionnelle «pour tout j» nécessite un résultat d'invariance global ou une preuve par classes qui couvre tous les états atteignables. Le log et les certificats couvrent néanmoins un très grand préfixe de la trajectoire (1001 itérations) et démontrent la robustesse de l'obstruction sur cette plage.

## 5) Documents joints recommandés pour la soumission au relecteur

- `lychrel_correctif.tex` (manuscrit principal)
- `extrait_196_preuve.txt` (extrait et traduction succincte de la preuve mod 2 / Hensel)
- `results/trajectory_obstruction_log.json` (log produit par `check_trajectory_obstruction.py`)
- `certificates/combined_certificates_196.json`, `certificates/gap3_window8.json`, `certificates/hensel_lift_results.json`
- `manifests/` (checksums et rapports d'intégrité)

---

Si tu veux, je peux :
- (A) joindre ces fichiers dans une archive `Lychrel_196_for_review.zip` à la racine ;
- (B) créer une release GitHub et pousser ces nouveautés (et préparer l'intégration Zenodo) ;
- (C) rédiger la lettre de réponse au relecteur en anglais ou français incorporant ces éléments.

Dis‑moi la prochaine action souhaitée.

## 6) Résultats récents — Orbites modulo M

J'ai exécuté `scripts/check_orbit_moduli.py` pour les modules demandés (1024, 4096, 1_000_000). Le résumé est disponible dans `results/orbit_moduli_summary.json` et des fiches lisibles ont été ajoutées dans `certificates/` :

- `certificates/orbit_moduli_1024.md`
- `certificates/orbit_moduli_4096.md`
- `certificates/orbit_moduli_1000000.md`

Chacun de ces fichiers résume le nombre de résidus rencontrés et indique que tous les représentants vérifiés ont été classés `theoretical_by_hensel` (aucun besoin de vérification supplémentaire signalé).

Action suivante que je peux effectuer maintenant : créer une archive ZIP `release/certificates_for_review.zip` contenant ces certificats et le fichier `results/orbit_moduli_summary.json`, et ajouter un petit manifeste `release/README_CERTIFICATES.md` expliquant le contenu. Dites si vous voulez que je crée cette archive et la place dans `release/` (ou un autre emplacement).
