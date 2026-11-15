"""Fetch and verify the pinned public Windows dependency kit; stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import urllib.request
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def entries():
    manifest = json.loads((ROOT / 'dependencias-publicas.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != 1:
        raise ValueError('Formato de manifiesto no compatible.')
    packages = manifest['packages'] + manifest['bootstrap']
    locked = {}
    for line in ((ROOT / 'requirements-publicas-win-py313.lock').read_text(encoding='utf-8') + (ROOT / 'requirements-bootstrap.lock').read_text(encoding='utf-8')).splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        match = re.fullmatch(r'([a-zA-Z0-9-]+)==([^ ]+) --hash=sha256:([0-9a-f]{64})', line)
        if not match:
            raise ValueError('Linea de bloqueo no compatible.')
        name, version, checksum = match.groups()
        if name in locked:
            raise ValueError('Dependencia repetida en el bloqueo.')
        locked[name] = (version, checksum)
    names, files = set(), set()
    for item in packages:
        filename = item['filename']
        if not re.fullmatch(r'[A-Za-z0-9_.+-]+', filename) or '/' in filename or '\\' in filename:
            raise ValueError('Nombre de archivo no valido en el manifiesto.')
        if filename in files or item['name'] in names:
            raise ValueError('Archivo o dependencia repetidos.')
        names.add(item['name']); files.add(filename)
        if locked.get(item['name']) != (item['version'], item['sha256']):
            raise ValueError('El manifiesto y el bloqueo no coinciden: ' + item['name'])
        url = urlparse(item['url'])
        if url.scheme != 'https' or url.hostname not in ('files.pythonhosted.org', 'github.com') or url.username or url.password:
            raise ValueError('Origen no permitido: ' + item['name'])
        if url.path.rsplit('/', 1)[-1] != filename:
            raise ValueError('El origen no coincide con el nombre fijado.')
        if item['kind'] == 'sdist':
            if item['name'] != 'htbuilder' or filename != 'htbuilder-0.9.0.tar.gz':
                raise ValueError('Solo htbuilder 0.9.0 admite construccion desde fuente.')
        elif item['kind'] != 'wheel' or not filename.endswith('.whl'):
            raise ValueError('Tipo de paquete no permitido.')
    if names != set(locked) or len(names) != 83:
        raise ValueError('El conjunto debe contener las 82 dependencias y pip fijados.')
    return packages


def verify(folder, packages):
    if not folder.is_dir():
        raise ValueError('No existe el directorio de paquetes: ' + str(folder))
    expected = {p['filename'] for p in packages}
    unexpected = sorted(p.name for p in folder.iterdir() if p.name not in expected)
    if unexpected:
        raise ValueError('El kit contiene archivos o directorios ajenos al manifiesto: ' + ', '.join(unexpected))
    errors = []
    for item in packages:
        path = folder / item['filename']
        if not path.is_file() or path.is_symlink():
            errors.append(item['filename'] + ': ausente o enlace simbolico')
        elif digest(path) != item['sha256']:
            errors.append(item['filename'] + ': SHA-256 incorrecto')
    if errors:
        raise ValueError('Kit incompleto o alterado:\n' + '\n'.join(errors))


def download(folder, packages):
    folder.mkdir(parents=True, exist_ok=True)
    for number, item in enumerate(packages, 1):
        path = folder / item['filename']
        if path.exists() or path.is_symlink():
            if not path.is_file() or path.is_symlink() or digest(path) != item['sha256']:
                raise ValueError('No se sobrescribe el archivo existente no valido: ' + str(path))
        else:
            pending = None
            try:
                request = urllib.request.Request(item['url'], headers={'User-Agent': 'Anonimizar-Dependencies/0.3.0'})
                with urllib.request.urlopen(request, timeout=60) as response, tempfile.NamedTemporaryFile(dir=folder, prefix='.descarga-', delete=False) as target:
                    pending = Path(target.name)
                    while chunk := response.read(1024 * 1024):
                        target.write(chunk)
                if digest(pending) != item['sha256']:
                    raise ValueError('SHA-256 incorrecto al descargar ' + item['filename'])
                # Windows rename does not replace an existing destination.
                if path.exists():
                    raise ValueError('El destino aparecio durante la descarga: ' + str(path))
                pending.rename(path)
            finally:
                if pending is not None and pending.exists():
                    pending.unlink()
        print(f'{number}/{len(packages)} verificado: {item["filename"]}', flush=True)
    verify(folder, packages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('accion', choices=['descargar', 'verificar'])
    parser.add_argument('--destino', type=Path, default=ROOT / 'wheelhouse')
    args = parser.parse_args()
    packages = entries()
    if args.accion == 'descargar':
        download(args.destino.resolve(), packages)
    else:
        verify(args.destino.resolve(), packages)
    print('Kit publico completo: 82 dependencias y pip con SHA-256 correcto.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print('Error de dependencias: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
