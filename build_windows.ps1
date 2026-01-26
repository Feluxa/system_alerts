$ErrorActionPreference = "Stop"

$IconPath = "assets/photos/photo.ico"

if (-not (Test-Path $IconPath)) {
    Write-Host "Icon not found at $IconPath. Create an .ico first (e.g. from photo.png) or adjust the path." -ForegroundColor Yellow
}

pyinstaller `
  --noconfirm `
  --onefile `
  --windowed `
  --icon $IconPath `
  main.py

Write-Host "Build complete. See dist/main.exe" -ForegroundColor Green
