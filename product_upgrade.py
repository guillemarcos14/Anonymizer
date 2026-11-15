"""Compatibility with previous releases; never changes the previous data."""
import json
import os
from pathlib import Path
import shutil
import sqlite3
import uuid
from contextlib import closing

# Previous on-disk identifiers are deliberately confined to compatibility code.
LEGACY_PRODUCT = 'Anonimous'
LEGACY_EXPORT_FORMAT = 'anonimous-history-v1'


def migrate_data(base=None):
    base = Path(base) if base else Path(os.environ['LOCALAPPDATA'])
    previous = base / LEGACY_PRODUCT
    target = base / 'Anonimizar'
    if target.exists() or not previous.is_dir():
        return False
    stage = base / ('Anonimizar-upgrade-' + uuid.uuid4().hex)
    stage.mkdir()
    settings = previous / 'settings.json'
    if settings.is_file():
        if not isinstance(json.loads(settings.read_text(encoding='utf-8')), dict):
            raise ValueError('No se pudieron conservar los ajustes anteriores: formato no válido.')
        shutil.copy2(settings, stage / settings.name)
    source = previous / 'documents.sqlite3'
    if source.is_file():
        with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as old:
            with closing(sqlite3.connect(stage / source.name)) as new:
                old.backup(new)
    recovery = previous / 'recovery'
    if recovery.is_dir():
        shutil.copytree(recovery, stage / 'recovery')
    (stage / 'upgrade.json').write_text(json.dumps({'version': '0.3.0', 'previous_data_preserved': True}), encoding='utf-8')
    stage.rename(target)
    return True


if __name__ == '__main__':
    migrate_data()
