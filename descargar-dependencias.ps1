param([string]$Python = 'python', [string]$Destino = (Join-Path $PSScriptRoot 'wheelhouse'))
$ErrorActionPreference = 'Stop'
& $Python -I (Join-Path $PSScriptRoot 'tools\dependencias.py') descargar --destino $Destino
if ($LASTEXITCODE -ne 0) { throw 'No se pudo obtener el kit publico completo. Corrige el error indicado y repite; no se cambian versiones ni hashes automaticamente.' }
