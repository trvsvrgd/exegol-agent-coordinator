param(
    [string]$IconPath = $env:EXEGOL_ICON_PATH
)

$ErrorActionPreference = "Stop"

if (-not $IconPath) {
    Write-Output "EXEGOL_ICON_PATH not set; skipping icon preparation."
    exit 0
}

if (-not (Test-Path $IconPath)) {
    Write-Error "Icon not found at $IconPath"
    exit 1
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Root
$AssetsDir = Join-Path $Root "assets"
$PngPath = Join-Path $AssetsDir "icon.png"
$IcoPath = Join-Path $AssetsDir "icon.ico"

New-Item -ItemType Directory -Path $AssetsDir -Force | Out-Null

Copy-Item -Path $IconPath -Destination $PngPath -Force

python - <<'PYCODE'
from PIL import Image
from pathlib import Path

png_path = Path("assets/icon.png")
ico_path = Path("assets/icon.ico")
img = Image.open(png_path)
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(ico_path, sizes=sizes)
print(f"Icon prepared at {ico_path}")
PYCODE
