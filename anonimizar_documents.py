"""Local history, reversible deletion and explicit legacy migration."""
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid
from contextlib import contextmanager, closing
from anonimizar_local import data_dir, read_settings
from product_upgrade import LEGACY_EXPORT_FORMAT

LOCAL_OWNER = "local"

def database_path():
    return Path(os.environ.get("ANONIMIZAR_DOCUMENTS_DB", data_dir() / "documents.sqlite3"))


@contextmanager
def connection():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        db.execute('CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, owner TEXT NOT NULL, title TEXT NOT NULL, payload TEXT NOT NULL, updated REAL NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS trash (id TEXT PRIMARY KEY, owner TEXT NOT NULL, title TEXT NOT NULL, payload TEXT NOT NULL, updated REAL NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS migrations (source TEXT NOT NULL, original_id TEXT NOT NULL, local_id TEXT NOT NULL, PRIMARY KEY(source, original_id))')
        with db:
            yield db
    finally:
        db.close()


def save(owner, payload, document_id=None):
    if owner != LOCAL_OWNER:
        raise ValueError("El historial de esta versión es local.")
    document_id = document_id or uuid.uuid4().hex
    title = ' '.join(payload['text'].split())[:70] or 'Documento sin título'
    with connection() as db:
        previous = db.execute('SELECT owner, title, payload FROM documents WHERE id=?', (document_id,)).fetchone()
        if previous and previous['owner'] != owner:
            raise ValueError('Documento no disponible.')
        if previous:
            title = previous['title']
        encoded = json.dumps(payload, ensure_ascii=False)
        if not previous or previous['payload'] != encoded:
            db.execute('INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?)', (document_id, owner, title, encoded, time.time()))
    return document_id


def rename_document(document_id, title):
    title = ' '.join(title.split())
    if not title or len(title) > 120:
        raise ValueError('Escribe un nombre de entre 1 y 120 caracteres.')
    with connection() as db:
        result = db.execute('UPDATE documents SET title=? WHERE owner=? AND id=?',
                            (title, LOCAL_OWNER, document_id))
        if not result.rowcount:
            raise ValueError('Ese documento ya no está disponible.')


def recent(owner):
    if not owner:
        return []
    with connection() as db:
        return [dict(row) for row in db.execute('SELECT id,title,updated FROM documents WHERE owner=? ORDER BY updated DESC', (owner,))]


def load(owner, document_id):
    with connection() as db:
        row = db.execute('SELECT payload FROM documents WHERE owner=? AND id=?', (owner, document_id)).fetchone()
    return json.loads(row['payload']) if row else None


def move_to_trash(document_id=None):
    where, params = ('owner=?', (LOCAL_OWNER,)) if document_id is None else ('owner=? AND id=?', (LOCAL_OWNER, document_id))
    with connection() as db:
        db.execute('INSERT OR REPLACE INTO trash SELECT * FROM documents WHERE ' + where, params)
        db.execute('DELETE FROM documents WHERE ' + where, params)


def restore_trash():
    with connection() as db:
        db.execute('INSERT OR IGNORE INTO documents SELECT * FROM trash WHERE owner=?', (LOCAL_OWNER,))
        db.execute('DELETE FROM trash WHERE owner=?', (LOCAL_OWNER,))


def trash_count():
    with connection() as db:
        return db.execute('SELECT COUNT(*) FROM trash WHERE owner=?', (LOCAL_OWNER,)).fetchone()[0]


def purge_trash():
    with connection() as db:
        db.execute('PRAGMA secure_delete=ON')
        db.execute('DELETE FROM trash WHERE owner=?', (LOCAL_OWNER,))


def export_history():
    with connection() as db:
        rows = db.execute('SELECT id,title,payload,updated FROM documents WHERE owner=? ORDER BY updated DESC', (LOCAL_OWNER,)).fetchall()
    return json.dumps({'format': 'anonimizar-history-v1', 'documents': [dict(r, payload=json.loads(r['payload'])) for r in rows]}, ensure_ascii=False, indent=2)


def legacy_path():
    return Path(os.environ.get('ANONIMIZAR_LEGACY_DB', read_settings().get('legacy_database', Path(__file__).parent / '.data/documents.sqlite3')))


def legacy_sources():
    path = legacy_path()
    if not path.is_file() or path.resolve() == database_path().resolve():
        return []
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        return db.execute('SELECT owner, COUNT(*) FROM documents GROUP BY owner ORDER BY owner').fetchall()


def migrate_legacy(owner):
    """Copy one collection; never rewrite source or merge unrelated owners."""
    source = legacy_path()
    if source.resolve() == database_path().resolve():
        raise ValueError('Origen y destino deben ser distintos.')
    with closing(sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True)) as old:
        rows = old.execute('SELECT id,title,payload,updated FROM documents WHERE owner=?', (owner,)).fetchall()
        snapshot = data_dir() / 'recovery' / 'legacy-documents.sqlite3'
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if not snapshot.exists():
            with closing(sqlite3.connect(snapshot)) as backup:
                old.backup(backup)
    count = 0
    source_key = str(source.resolve()) + '|' + owner
    with connection() as db:
        for original_id, title, payload, updated in rows:
            json.loads(payload)
            if db.execute('SELECT 1 FROM migrations WHERE source=? AND original_id=?', (source_key, original_id)).fetchone():
                continue
            local_id = uuid.uuid5(uuid.NAMESPACE_URL, source_key + '|' + original_id).hex
            db.execute('INSERT INTO documents VALUES (?,?,?,?,?)', (local_id, LOCAL_OWNER, title, payload, updated))
            db.execute('INSERT INTO migrations VALUES (?,?,?)', (source_key, original_id, local_id))
            count += 1
    return count


def import_history(raw):
    value = json.loads(raw)
    if not isinstance(value, dict) or value.get('format') not in ('anonimizar-history-v1', LEGACY_EXPORT_FORMAT) or not isinstance(value.get('documents'), list):
        raise ValueError('La copia no es un historial de Anonimizar.')
    documents = value['documents']
    for row in documents:
        if not isinstance(row, dict) or not isinstance(row.get('payload'), dict):
            raise ValueError('La copia contiene un documento no válido.')
        payload = row['payload']
        title = row.get('title')
        if title is not None and not isinstance(title, str):
            raise ValueError('La copia contiene un nombre de documento no válido.')
        if not isinstance(payload.get('text'), str) or len(payload['text']) > 10000:
            raise ValueError('La copia contiene un documento no válido.')
        if not isinstance(payload.get('settings', {}), dict) or not isinstance(payload.get('review', {}), dict):
            raise ValueError('La copia contiene ajustes no válidos.')
    with connection() as db:
        for row in documents:
            payload = row['payload']
            fingerprint = 'import|' + json.dumps(payload, sort_keys=True)
            identifier = uuid.uuid5(uuid.NAMESPACE_URL, fingerprint).hex
            try:
                identifier = uuid.UUID(row.get('id', '')).hex
            except (ValueError, AttributeError, TypeError):
                pass
            previous = db.execute('SELECT payload FROM documents WHERE id=?', (identifier,)).fetchone()
            if previous and json.loads(previous['payload']) != payload:
                identifier = uuid.uuid5(uuid.NAMESPACE_URL, fingerprint).hex
            title = ' '.join((row.get('title') or '').split()) or ' '.join(payload['text'].split())[:70] or 'Documento sin título'
            db.execute('INSERT OR IGNORE INTO documents VALUES (?,?,?,?,?)', (identifier, LOCAL_OWNER, title, json.dumps(payload, ensure_ascii=False), time.time()))
    return len(documents)
