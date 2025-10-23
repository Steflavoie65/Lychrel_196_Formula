# Reproduce certificates summary
# Computes SHA256 for key certificate files referenced in the manuscript
# Usage: run this script from the repository root or directly; it locates the repo root automatically.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

Write-Host "Repository root: $repoRoot"

# Explicit files referenced in the manuscript (relative paths)
$relativeExplicit = @(
    'validation_results_aext1.json',
    'validation_results_aext2.json',
    'validation_results_aext3.json',
    'validation_results_aext4.json',
    'validation_results_aext5.json',
    'validation_results_class_III.json',
    'validation_results_aext9.json',
    'verifier\hensel_lift_results.json',
    'verifier\gap3_window8.json',
    'verifier\combined_certificates_196.json'
)

$explicit = @()
foreach ($rel in $relativeExplicit) {
    $explicit += Join-Path $repoRoot $rel
}

# Patterns (test files may be placed either at repo root or in IMPORTANT/ or verifier/)

$patterns = @('test_3gaps*.json','test_extensions*.json','test_*20251020*.json')

$foundPatternFiles = Get-ChildItem -Path $repoRoot -Include $patterns -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }

$allCandidates = ($explicit + $foundPatternFiles) | Sort-Object -Unique

$summary = @()

foreach ($f in $allCandidates) {
    if (Test-Path $f) {
        try {
            $h = Get-FileHash -Algorithm SHA256 $f
            $line = "OK | $($h.Hash) | $f"
            Write-Host $line
            $summary += $line
        } catch {
            $line = "ERR | unable to hash | $f"
            Write-Host $line
            $summary += $line
        }
    } else {
        $line = "MISSING | - | $f"
        Write-Host $line
        $summary += $line
    }
}

# Also list other verifier scripts referenced

$scriptRel = @(
    'verifier\validate_aext5.py',
    'verifier\verify_196_mod2.py',
    'verifier\verify_196_modk.py',
    'verifier\test_gap123.py',
    'verifier\test_extensions.py',
    'verifier\prove_a_ext_196.py'
)

foreach ($rel in $scriptRel) {
    $s = Join-Path $repoRoot $rel
    if (Test-Path $s) {
        $h = Get-FileHash -Algorithm SHA256 $s
        $line = "SCRIPT | $($h.Hash) | $s"
        Write-Host $line
        $summary += $line
    } else {
        $line = "SCRIPT-MISSING | - | $s"
        Write-Host $line
        $summary += $line
    }
}

# Write summary file
$summaryFile = Join-Path $repoRoot 'verifier\reproduce_summary.txt'
$summary | Out-File -FilePath $summaryFile -Encoding UTF8
Write-Host "\nSummary written to: $summaryFile"
