param(
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"

$WixCandle = Get-Command "candle.exe" -ErrorAction SilentlyContinue
$WixLight = Get-Command "light.exe" -ErrorAction SilentlyContinue

if (-not $WixCandle -or -not $WixLight) {
    Write-Error "WiX Toolset not found in PATH. Install WiX v3 and retry."
    exit 1
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Root
$InstallerDir = Join-Path $Root "installer"
$BuildDir = Join-Path $InstallerDir "build"
$DistDir = Join-Path $InstallerDir "dist"

New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null
New-Item -ItemType Directory -Path $DistDir -Force | Out-Null

Push-Location $Root
& .\scripts\prepare_icon.ps1
if (-not (Test-Path "dist\exegol\exegol.exe")) {
    Write-Error "Missing dist\exegol\exegol.exe. Run .\scripts\build_exe.ps1 first."
    Pop-Location
    exit 1
}
Pop-Location

Push-Location $InstallerDir
& $WixCandle.Source -dExegolVersion=$Version -o "$BuildDir\exegol.wixobj" ".\exegol.wxs"
& $WixLight.Source -o "$DistDir\exegol-$Version.msi" "$BuildDir\exegol.wixobj"
Pop-Location

Write-Output "MSI created at installer\dist\exegol-$Version.msi"
