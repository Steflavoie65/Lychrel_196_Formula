Lychrel_Preuve_complete

This package contains the core artifacts necessary to reproduce the computational evidence and selected proofs for the 196 manuscript.

Structure:
- tex/: main TeX source and small inserts
- pdf/: compiled PDF
- scripts/: verification scripts to reproduce runs
- certificates/: machine-readable JSON certificates produced by the verifier
- results/: selected JSON run outputs used in the paper
- manifests/: bookkeeping and checksum reports
- proofs_and_notes/: supportive notes and annexes (if present)
- portes/: selected 'portes' data files

Quick reproduction (PowerShell, from package root):
1) Run critical verifiers (example):
   python scripts\verify_196_mod2.py
   python scripts\check_jacobian_mod2.py
   python scripts\test_gap123.py --iterations 10000

2) Recreate checksums: generate_checksums.py or use supplied manifest_sha256.txt

If you need a different selection or more files (big porte files), ask and I will update the package.
