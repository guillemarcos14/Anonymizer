[English](INSTALLATION.md) | **Español**

# Instalación reproducible — Windows 0.3.0

Este proceso obtiene las dependencias y el modelo desde fuentes públicas, sin usar la carpeta auxiliar, la instalación original, una caché de pip ni un entorno previo. No publica el producto ni cambia las 82 versiones de ejecución.

Esta guía cubre la instalación desde el código. Para instalar la aplicación sin un entorno de desarrollo, utiliza el [instalador de Windows y los pasos de inicio](README.es.md#instalar-y-empezar). La interfaz y el procesamiento están orientados a textos en español.

## Requisitos

Windows x64 y [CPython 3.13.7, instalador oficial de 64 bits](https://www.python.org/downloads/release/python-3137/), con soporte `venv`. Esta es la versión fijada para reproducir 0.3.0; no se está declarando la versión más reciente ni una recomendación general de seguridad. No elegir ARM64, 32 bits o la edición free-threaded. El navegador será la ventana de la aplicación.

Se necesita Internet para descargar el kit. La instalación posterior usa únicamente ese kit local. Reservar al menos 1 GiB para entorno y paquetes; la construcción del instalador necesita espacio adicional. Python se instala por separado: los scripts no instalan ni actualizan el Python del sistema.

## Preparar y abrir

Desde PowerShell, situado en la carpeta del repositorio:

```powershell
.\descargar-dependencias.ps1 -Python 'C:\ruta\Python313\python.exe'
.\instalar.ps1 -Python 'C:\ruta\Python313\python.exe'
.\iniciar.ps1
```

1. `descargar-dependencias.ps1` obtiene 83 archivos: 81 wheels del producto, la fuente de `htbuilder` y el wheel de `pip` fijado. Verifica cada SHA-256 y guarda el kit en `wheelhouse/`, excluido de Git. No sustituye un archivo existente con hash incorrecto; conserva el archivo para diagnosticar. Repetir una descarga reutiliza solo los archivos que coinciden.
2. `instalar.ps1` comprueba CPython 3.13.7 x64 y valida el kit completo antes de crear `.venv`. Rechaza un entorno existente y archivos ajenos al manifiesto. Fija `pip` 26.0.1 y después instala las 82 versiones con hashes, sin índice ni caché. Solo `htbuilder` se construye desde fuente, en aislamiento, con `setuptools` 84.2.1 disponible en el mismo kit. No hace falta compilador C para ese paquete Python.
3. La instalación ejecuta `pip check`, verifica las 82 versiones y carga el modelo para sustituir un correo y un teléfono ficticios, conservando un importe. Esta comprobación usa la lista de dominios incluida, sin actualizarla; no altera el comportamiento de la aplicación real ni certifica privacidad o calidad general.
4. `iniciar.ps1` usa `.venv` de esta carpeta. Para detener el motor, usar **Configuración → Cerrar Anonimizar y detener el motor**. Cerrar solo la pestaña no lo detiene.

Las rutas de Python de los ejemplos se sustituyen por el ejecutable real. No ejecutar los comandos si falla el anterior. Si PowerShell bloquea scripts por su política local, revisar la política del equipo; estos scripts no la cambian ni solicitan privilegios de administrador.

## Usar un kit en otro directorio o equipo sin red

En el equipo con Internet:

```powershell
.\descargar-dependencias.ps1 -Python 'C:\ruta\Python313\python.exe' -Destino 'C:\kits\anonimizar-0.3.0'
```

Copiar el repositorio y el directorio de paquetes al equipo Windows x64 con CPython 3.13.7 ya instalado. Allí, desde la carpeta del repositorio:

```powershell
.\instalar.ps1 -Python 'C:\ruta\Python313\python.exe' -Paquetes 'C:\kits\anonimizar-0.3.0'
```

También existe `-Entorno` para instalar en una ruta nueva de prueba. `iniciar.ps1` y el empaquetador siguen buscando `.venv` dentro del repositorio; un entorno con otro nombre no cambia esas rutas automáticamente. No sobrescribir un entorno anterior para repetir una prueba.

## Qué se fija y por qué hay dos bloqueos

| Archivo | Función |
|---|---|
| [dependencias-publicas.json](dependencias-publicas.json) | Nombres, versiones, URLs HTTPS y SHA-256 de las 82 dependencias y de pip |
| [requirements-publicas-win-py313.lock](requirements-publicas-win-py313.lock) | Instalación actual: 82 versiones y hashes de los artefactos públicos |
| [requirements-bootstrap.lock](requirements-bootstrap.lock) | pip 26.0.1, herramienta de instalación fijada |
| [requirements-win-py313.lock](requirements-win-py313.lock) y [wheelhouse-sha256.json](wheelhouse-sha256.json) | Registro histórico intacto del kit anterior, con su wheel local de htbuilder |
| [requirements-directas.txt](requirements-directas.txt) | Referencia de dependencias directas; no sustituye al bloqueo completo |

La revisión del 15/11/2026 confirmó 80 wheels de PyPI por nombre y SHA-256, y descargó [el modelo oficial xx_ent_wiki_sm 3.8.0 de Explosion](https://github.com/explosion/spacy-models/releases/tag/xx_ent_wiki_sm-3.8.0) con el hash histórico esperado.

[PyPI publica htbuilder 0.9.0 como fuente](https://pypi.org/pypi/htbuilder/0.9.0/json), sin el wheel del kit local anterior. El bloqueo público conserva `htbuilder==0.9.0` y verifica el tar.gz oficial con SHA-256 `58c0bc5502c1a46b42ae9e074c43ec0f6fdc24ed334936cb17e1ed5a8938aee2`. El hash del wheel generado localmente puede variar; no se promete identidad byte a byte con el instalador anterior. No se acepta otra versión ni una fuente sin hash como alternativa automática.

El modelo se instala desde su wheel descargado; no se ejecuta `spacy download` ni se cambia el modelo configurado. Los avisos y licencias se conservan en [LICENCIAS.md](LICENCIAS.md). Las fuentes oficiales de referencia del proceso son [pip download](https://pip.pypa.io/en/stable/cli/pip_download/) y [verificación de hashes de pip](https://pip.pypa.io/en/stable/topics/secure-installs/).

## Verificar y diagnosticar

```powershell
python -I tools\dependencias.py verificar
.\.venv\Scripts\python.exe -I tools\verificar_instalacion.py
python -B -m unittest discover -s tests -v
```

Usar CPython 3.13.7 en el primer y tercer comando si `python` del PATH señala a otra versión. El primer comando comprueba el kit, el segundo versiones y prueba sintética, y el tercero verifica rechazo de corrupción, archivos ajenos y sustitución de archivos inválidos.

Un error de descarga debe resolverse comprobando conexión y disponibilidad del origen indicado; no eliminar hashes ni cambiar versiones para saltarlo. Un archivo alterado o inesperado se conserva: usar un directorio nuevo de kit o revisar el archivo antes de retirarlo. Un fallo de instalación conserva el entorno para diagnóstico; elegir otra ruta nueva para reintentar. No se inspeccionan documentos del usuario en la prueba sintética.

La disponibilidad de los servidores públicos puede cambiar. Las instrucciones permiten reconstruir el entorno con los mismos artefactos de entrada mientras se conserven o sigan disponibles; no garantizan disponibilidad perpetua ni equivalencia binaria del instalador. La prueba en otro equipo y la reconstrucción del instalador son controles separados en [PREPARACION.md](PREPARACION.md).
