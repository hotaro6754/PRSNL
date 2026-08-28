param (
    [string]$Command
)

if ($Command -eq "production-audit") {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║          CYBEROS PRODUCTION AUDIT          ║" -ForegroundColor Cyan
    Write-Host "╠════════════════════════════════════════════╣" -ForegroundColor Cyan
    
    # Run the test orchestrator
    python tests_external/run_audit.py
    $auditExitCode = $LASTEXITCODE

    Write-Host "Generating Reports..." -ForegroundColor Yellow
    python tests_external/reporting/generator.py

    if ($auditExitCode -ne 0) {
        Write-Host "║ AUDIT FAILED - FAILING CLOSED              ║" -ForegroundColor Red
        Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
        exit 1
    } else {
        Write-Host "║ AUDIT PASSED                               ║" -ForegroundColor Green
        Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    }
}
elseif ($Command -eq "lab-e2e") {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║             CYBEROS LAB E2E                ║" -ForegroundColor Cyan
    Write-Host "╠════════════════════════════════════════════╣" -ForegroundColor Cyan
    Write-Host "Executing gold-standard test..." -ForegroundColor Yellow
    
    python -m pytest tests_external/e2e/test_lab_e2e.py -v
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nGolden scenario TEST-E2E-001 passed." -ForegroundColor Green
    } else {
        Write-Host "`nGolden scenario TEST-E2E-001 failed." -ForegroundColor Red
        exit 1
    }
}
elseif ($Command -eq "report") {
    if ($args.Count -eq 0) {
        Write-Host "Usage: .\cyberos.ps1 report [incident <id> | technical]"
        exit 1
    }
    $SubCommand = $args[0]
    if ($SubCommand -eq "incident") {
        $IncidentId = $args[1]
        Write-Host "Generating Incident Report for $IncidentId..." -ForegroundColor Yellow
        python tests_external/reporting/incident.py $IncidentId
    } elseif ($SubCommand -eq "technical") {
        Write-Host "Generating Technical Report..." -ForegroundColor Yellow
        python tests_external/reporting/generator.py
    } else {
        Write-Host "Unknown report command." -ForegroundColor Red
    }
}
else {
    Write-Host "Usage: .\cyberos.ps1 [production-audit|lab-e2e|report]"
}
