param([string]$Python = 'python', [string]$Entorno = '.venv', [string]$Paquetes = (Join-Path $PSScriptRoot 'wheelhouse'))
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & $Python -I -c "import sys,platform; assert sys.version_info[:3]==(3,13,7) and sys.platform=='win32' and platform.machine()=='AMD64', 'Se requiere CPython 3.13.7 Windows x64'"
    if ($LASTEXITCODE -ne 0) { throw 'Python incompatible' }
    if (Test-Path -LiteralPath $Entorno) { throw "El entorno ya existe: $Entorno. Elige otro nombre; no se sobrescribe." }
    & $Python -I (Join-Path $PSScriptRoot 'tools\dependencias.py') verificar --destino $Paquetes
    if ($LASTEXITCODE -ne 0) { throw 'Kit publico incompleto o alterado. Ejecuta descargar-dependencias.ps1. No se ha creado el entorno.' }
    $paquetesResueltos = (Resolve-Path -LiteralPath $Paquetes).Path
    & $Python -I -m venv $Entorno
    if ($LASTEXITCODE -ne 0) { throw 'Error al crear el entorno' }
    $entornoPython = Join-Path $Entorno 'Scripts\python.exe'
    & $entornoPython -I -m pip --isolated --disable-pip-version-check install --no-cache-dir --no-index --find-links $paquetesResueltos --only-binary=:all: --require-hashes --force-reinstall -r requirements-bootstrap.lock
    if ($LASTEXITCODE -ne 0) { throw 'Error al fijar la version de pip' }
    & $entornoPython -I -m pip --isolated --disable-pip-version-check install --no-cache-dir --no-index --find-links $paquetesResueltos --only-binary=:all: --no-binary=htbuilder --require-hashes -r requirements-publicas-win-py313.lock
    if ($LASTEXITCODE -ne 0) { throw 'Error de instalacion; conserva el entorno y el registro para diagnosticar' }
    & $entornoPython -I -m pip --isolated --disable-pip-version-check check
    if ($LASTEXITCODE -ne 0) { throw 'Dependencias incompatibles' }
    & $entornoPython -I (Join-Path $PSScriptRoot 'tools\verificar_instalacion.py')
    if ($LASTEXITCODE -ne 0) { throw 'La comprobacion del modelo o del motor no ha terminado correctamente' }
} finally { Pop-Location }
