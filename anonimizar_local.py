"""Per-user local configuration. No accounts or network calls."""
import json
import os
from pathlib import Path
import tempfile

VERSION = '0.3.0'
PREFERENCE_KEYS = ('doc_operator', 'doc_threshold', 'doc_explanations', 'doc_mask_count', 'doc_mask_char', 'doc_entities')

def data_dir():
    override = os.environ.get('ANONIMIZAR_DATA_DIR')
    return Path(override) if override else Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local/share')) / 'Anonimizar'

def read_settings():
    try:
        value = json.loads((data_dir() / 'settings.json').read_text(encoding='utf-8'))
        if not isinstance(value, dict):
            raise ValueError('Formato de configuraciÃ³n no vÃ¡lido')
        if not isinstance(value.get('preferences', {}), dict):
            raise ValueError('Preferencias locales no vÃ¡lidas')
        if not isinstance(value.get('history_enabled', True), bool):
            raise ValueError('OpciÃ³n de historial no vÃ¡lida')
        return value
    except FileNotFoundError:
        return {}

def write_settings(value):
    root = data_dir()
    root.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='settings-', suffix='.tmp', dir=root)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as target:
            json.dump(value, target, ensure_ascii=False, indent=2)
        os.replace(name, root / 'settings.json')
    finally:
        Path(name).unlink(missing_ok=True)

def update_settings(**changes):
    settings = read_settings()
    settings.update(changes)
    write_settings(settings)

def history_enabled():
    return read_settings().get('history_enabled', True) is True

def save_preferences(state):
    # Working text, free-text lists and encryption keys never enter preferences.
    values = {key: state[key] for key in PREFERENCE_KEYS if key in state}
    settings = read_settings()
    if settings.get('preferences') != values:
        settings['preferences'] = values
        write_settings(settings)
