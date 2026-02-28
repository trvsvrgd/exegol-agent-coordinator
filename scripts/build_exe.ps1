param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

& $Python -m pip install -r requirements.txt
& .\scripts\prepare_icon.ps1
& $Python -m PyInstaller exegol.spec

Write-Output "Build complete. Find the .exe in .\dist\exegol\exegol.exe"
