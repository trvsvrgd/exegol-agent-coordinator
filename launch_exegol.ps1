param(
    [string]$Python = "python"
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExePath = Join-Path $Root "dist\exegol\exegol.exe"

if (Test-Path $ExePath) {
    Start-Process $ExePath
    exit 0
}

$VenvPython = Join-Path $Root "venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    & $VenvPython -m streamlit run (Join-Path $Root "ui_dashboard.py")
    exit 0
}

& $Python -m streamlit run (Join-Path $Root "ui_dashboard.py")
