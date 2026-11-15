param([int]$Puerto = 8502)
$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Entorno de desarrollo no instalado. Para usar Anonimizar, ejecuta el instalador de dist-local.' }
Start-Process -FilePath $python -ArgumentList @(('"' + (Join-Path $PSScriptRoot 'anonimizar_launcher.py') + '"'), '--port', $Puerto) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
