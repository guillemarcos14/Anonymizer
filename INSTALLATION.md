**English** | [Español](INSTALACION.md)

# Reproducible installation — Windows 0.3.0

This process obtains dependencies and the model from public sources without using the auxiliary preparation folder, the original installation, a pip cache or an existing environment. It does not publish the product or change its 82 runtime package versions.

This guide covers installation from source. To install the app without a development environment, use the [Windows installer and getting-started instructions](README.md#install-and-get-started). The app interface and text-processing workflow are in Spanish.

## Requirements

Windows x64 and [CPython 3.13.7, official 64-bit installer](https://www.python.org/downloads/release/python-3137/), with `venv` support. This is the pinned version for reproducing 0.3.0, not a claim that it is the latest version or a general security recommendation. Do not choose ARM64, 32-bit or the free-threaded edition. The browser serves as the app's window.

Internet access is needed to download the kit. Subsequent installation uses only that local kit. Allow at least 1 GiB for the environment and packages; building the installer requires additional space. Install Python separately: these scripts do not install or update system Python.

## Prepare and open

From PowerShell in the repository directory:

```powershell
.\descargar-dependencias.ps1 -Python 'C:\path\Python313\python.exe'
.\instalar.ps1 -Python 'C:\path\Python313\python.exe'
.\iniciar.ps1
```

1. `descargar-dependencias.ps1` obtains 83 files: 81 product wheels, the `htbuilder` source distribution and the pinned `pip` wheel. It checks every SHA-256 and saves the kit in `wheelhouse/`, which is excluded from Git. It does not replace an existing file with an incorrect hash; that file is kept for diagnosis. Repeating the download reuses only matching files.
2. `instalar.ps1` checks CPython 3.13.7 x64 and validates the entire kit before creating `.venv`. It rejects an existing environment and files not listed in the manifest. It pins `pip` 26.0.1, then installs the 82 package versions with hashes, without an index or cache. Only `htbuilder` is built from source, in isolation, using `setuptools` 84.2.1 from the same kit. That Python package does not require a C compiler.
3. Installation runs `pip check`, verifies all 82 versions and loads the model to replace a fictional email address and phone number while preserving an amount. This check uses the included domain list without updating it; it does not change the real app's behavior or certify privacy or general detection quality.
4. `iniciar.ps1` uses this directory's `.venv`. To stop the engine, use **Configuración → Cerrar Anonimizar y detener el motor** in the Spanish interface. Closing the browser tab alone does not stop it.

Replace the example Python paths with the actual executable. Do not continue to the next command if the previous one fails. If PowerShell blocks scripts because of local policy, review the computer's policy; these scripts do not change it or request administrator privileges.

## Use a kit in another directory or on an offline computer

On the computer with Internet access:

```powershell
.\descargar-dependencias.ps1 -Python 'C:\path\Python313\python.exe' -Destino 'C:\kits\anonimizar-0.3.0'
```

Copy the repository and package directory to the Windows x64 computer with CPython 3.13.7 already installed. On that computer, from the repository directory:

```powershell
.\instalar.ps1 -Python 'C:\path\Python313\python.exe' -Paquetes 'C:\kits\anonimizar-0.3.0'
```

The `-Entorno` parameter also allows installation into a new test-environment path. `iniciar.ps1` and the packager still look for `.venv` inside the repository; a differently named environment does not automatically change those paths. Do not overwrite an earlier environment to repeat a test.

## What is pinned and why there are two dependency locks

| File | Purpose |
|---|---|
| [dependencias-publicas.json](dependencias-publicas.json) | Names, versions, HTTPS URLs and SHA-256 hashes for the 82 dependencies and pip |
| [requirements-publicas-win-py313.lock](requirements-publicas-win-py313.lock) | Current installation: 82 versions and hashes of public artifacts |
| [requirements-bootstrap.lock](requirements-bootstrap.lock) | pip 26.0.1, the pinned installation tool |
| [requirements-win-py313.lock](requirements-win-py313.lock) and [wheelhouse-sha256.json](wheelhouse-sha256.json) | Unchanged historical record of the previous kit, including its locally built htbuilder wheel |
| [requirements-directas.txt](requirements-directas.txt) | Reference list of direct dependencies; it does not replace the complete lock file |

The November 15, 2026 check confirmed 80 PyPI wheels by filename and SHA-256, and downloaded [Explosion's official xx_ent_wiki_sm 3.8.0 model](https://github.com/explosion/spacy-models/releases/tag/xx_ent_wiki_sm-3.8.0) with the expected historical hash.

[PyPI publishes htbuilder 0.9.0 as a source distribution](https://pypi.org/pypi/htbuilder/0.9.0/json), without the wheel from the earlier local kit. The public lock keeps `htbuilder==0.9.0` and verifies the official tar.gz with SHA-256 `58c0bc5502c1a46b42ae9e074c43ec0f6fdc24ed334936cb17e1ed5a8938aee2`. The locally built wheel's hash may vary; byte-for-byte identity with the earlier installer is not promised. No alternative version or unhashed source is accepted automatically.

The model is installed from its downloaded wheel; `spacy download` is not run and the configured model is not changed. Notices and licenses are preserved in [LICENCIAS.md (Spanish)](LICENCIAS.md). Official process references are [pip download](https://pip.pypa.io/en/stable/cli/pip_download/) and [pip hash verification](https://pip.pypa.io/en/stable/topics/secure-installs/).

## Verify and diagnose

```powershell
python -I tools\dependencias.py verificar
.\.venv\Scripts\python.exe -I tools\verificar_instalacion.py
python -B -m unittest discover -s tests -v
```

Use CPython 3.13.7 for the first and third commands if `python` on PATH points to another version. The first command checks the kit, the second checks versions and the synthetic example, and the third tests rejection of corruption, unapproved files and replacement of invalid existing files.

For a download error, check the connection and availability of the reported source; do not remove hashes or change versions to bypass it. An altered or unexpected file is preserved: use a new kit directory or inspect the file before removing it. A failed installation keeps the environment for diagnosis; choose another new path for a retry. The synthetic check does not inspect user documents.

Public server availability can change. These instructions reproduce the environment with the same input artifacts while those artifacts are retained or remain available; they do not guarantee perpetual availability or binary equivalence of the installer. Testing on another computer and rebuilding the installer are separate checks recorded in [PREPARACION.md (Spanish)](PREPARACION.md).
