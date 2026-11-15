"""Build offline Windows installer from the already verified local environment.

No user databases, OAuth configuration, secrets, or working documents are bundled.
"""
import hashlib
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from anonimizar_local import VERSION

OUTPUT = ROOT / 'dist-local'
CSC = Path(os.environ['WINDIR']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
MODULES = ['presidio_streamlit.py', 'presidio_branding.py', 'presidio_helpers.py',
           'presidio_analyzer_config.py', 'identidades.py', 'identidades_ui.py',
           'phone_boundaries.py', 'anonimizar_documents.py', 'anonimizar_local.py',
           'anonimizar_local_ui.py', 'anonimizar_server.py', 'anonimizar_workspace.py',
           'anonimizar_launcher.py', 'anonimizar_appearance.py', 'product_upgrade.py']


def compile_cs(source, target, resources=()):
    command = [str(CSC), '/nologo', '/target:winexe', '/platform:x64', '/optimize+',
               '/win32icon:' + str(OUTPUT / 'anonimizar.ico'),
               '/win32manifest:' + str(ROOT / 'packaging/app.manifest'),
               '/reference:System.Windows.Forms.dll', '/reference:System.IO.Compression.dll',
               '/reference:System.IO.Compression.FileSystem.dll', '/reference:System.Web.Extensions.dll', '/out:' + str(target)]
    command.extend('/resource:' + str(path) + ',' + name for path, name in resources)
    subprocess.run(command + [str(ROOT / 'packaging/InstallScope.cs'), str(source)], check=True)


def digest_file(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def main():
    if (sys.version_info[:3] != (3, 13, 7) or sys.platform != 'win32'
            or platform.machine() != 'AMD64'
            or Path(sys.prefix).resolve() != (ROOT / '.venv').resolve()):
        raise RuntimeError('Construir con CPython 3.13.7 x64 desde la .venv de esta copia.')
    import importlib.metadata
    expected = json.loads((ROOT / 'dependencias-publicas.json').read_text(encoding='utf-8'))
    for item in expected['packages'] + expected['bootstrap']:
        if importlib.metadata.version(item['name']) != item['version']:
            raise RuntimeError('Version de dependencia no valida para construir: ' + item['name'])
    OUTPUT.mkdir(exist_ok=True)
    import shutil
    shutil.copy2(ROOT / 'assets/anonimizar-app.ico', OUTPUT / 'anonimizar.ico')
    compile_cs(ROOT / 'packaging/Launcher.cs', OUTPUT / 'Anonimizar.exe')
    compile_cs(ROOT / 'packaging/Uninstall.cs', OUTPUT / 'Desinstalar.exe')
    entries = []
    def include(path, archive):
        if not path.is_file():
            raise FileNotFoundError(f'Recurso requerido ausente: {path}')
        if '__pycache__' not in path.parts and path.suffix not in ('.pyc', '.pyo'):
            entries.append((path, str(archive).replace('\\', '/')))
    for name in MODULES + ['anonimizar.css', 'product-ui.css', 'workspace.css', 'anonimizar-icon.svg', 'LOCAL.md', 'LICENCIAS.md', 'CONDICIONES-ENTREGA.md', 'README.md', 'README.es.md', 'PREPARACION.md', 'INSTALACION.md', 'INSTALADOR.md',
                           'dependencias-publicas.json', 'requirements-publicas-win-py313.lock',
                           'requirements-bootstrap.lock', 'requirements-directas.txt', 'requirements-win-py313.lock',
                           'wheelhouse-sha256.json', 'instalar.ps1', 'iniciar.ps1', 'descargar-dependencias.ps1']:
        include(ROOT / name, Path('app') / name)
    for folder in ('assets', 'config', 'avisos', '.streamlit', 'tools', 'tests', 'packaging', 'docs/images'):
        for path in (ROOT / folder).rglob('*'):
            if not path.is_file():
                continue
            if folder == '.streamlit' and path.name != 'config.toml':
                continue
            if path.name == 'oauth-popup.js' or path.name == 'oauth.toml' or path.name == 'secrets.toml':
                continue
            include(path, Path('app') / path.relative_to(ROOT))
    base = Path(sys.base_prefix)
    for path in base.iterdir():
        if path.suffix in ('.exe', '.dll') or path.name == 'LICENSE.txt':
            include(path, Path('runtime') / path.name)
    for folder in ('Lib', 'DLLs'):
        for path in (base / folder).rglob('*'):
            if not path.is_file():
                continue
            if 'site-packages' in path.relative_to(base).parts:
                continue
            include(path, Path('runtime') / path.relative_to(base))
    for path in (ROOT / '.venv/Lib/site-packages').rglob('*'):
        if not path.is_file():
            continue
        include(path, Path('runtime/Lib/site-packages') / path.relative_to(ROOT / '.venv/Lib/site-packages'))
    for name in ('Anonimizar.exe', 'Desinstalar.exe'):
        include(OUTPUT / name, Path(name))
    names = [name for _, name in entries]
    if len(names) != len(set(names)):
        raise RuntimeError('El paquete contiene rutas duplicadas.')
    manifest = {}
    payload = OUTPUT / 'payload.zip'
    pending_payload = OUTPUT / 'payload.pending.zip'
    with zipfile.ZipFile(pending_payload, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        for path, name in entries:
            archive.write(path, name)
            with path.open('rb') as source:
                manifest[name] = hashlib.file_digest(source, 'sha256').hexdigest()
        archive.writestr('manifest.json', json.dumps(manifest, indent=2))
    pending_payload.replace(payload)
    digest = hashlib.file_digest(payload.open('rb'), 'sha256').hexdigest()
    setup_source = OUTPUT / 'Setup.generated.cs'
    setup_source.write_text((ROOT / 'packaging/Setup.cs').read_text(encoding='utf-8').replace('__VERSION__', VERSION).replace('__HASH__', digest), encoding='utf-8')
    target = OUTPUT / f'Anonimizar-Setup-{VERSION}-win-x64.exe'
    compile_cs(setup_source, target, [(payload, 'payload.zip')])
    (OUTPUT / f'Anonimizar-Setup-{VERSION}-win-x64.exe.sha256').write_text(digest_file(target) + '  ' + target.name + '\n', encoding='utf-8')
    (OUTPUT / 'build.json').write_text(json.dumps({'version': VERSION, 'installer': str(target), 'sha256': hashlib.file_digest(target.open('rb'), 'sha256').hexdigest(), 'files': len(entries), 'payload_sha256': digest}, indent=2), encoding='utf-8')
    print(str(target), flush=True)


if __name__ == '__main__':
    main()
