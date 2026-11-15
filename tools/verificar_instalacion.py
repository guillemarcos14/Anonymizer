"""Check pinned versions, installed model and synthetic detection without user data."""
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    expected = json.loads((ROOT / 'dependencias-publicas.json').read_text(encoding='utf-8'))['packages']
    for item in expected:
        actual = importlib.metadata.version(item['name'])
        if actual != item['version']:
            raise ValueError(f'{item["name"]}: se esperaba {item["version"]}, instalado {actual}')
    with tempfile.TemporaryDirectory(prefix='anonimizar-verificacion-') as folder:
        os.environ['TLDEXTRACT_CACHE'] = folder
        os.environ['ANONIMIZAR_DATA_DIR'] = folder
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        # The installed Public Suffix snapshot avoids fetching a domain list for this test.
        import tldextract
        from types import SimpleNamespace
        import presidio_analyzer.predefined_recognizers.generic.email_recognizer as email_module
        # Force the same library snapshot path for the synthetic check only.
        email_module.tldextract = SimpleNamespace(extract=tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None))
        from presidio_analyzer_config import create_analyzer_engine
        from identidades import resolve_spans, default_assignments, render_identities
        engine = create_analyzer_engine('spacy', 'xx_ent_wiki_sm')
        text = 'Ejemplo ficticio. Correo: prueba@example.com. Telefono: 612345678. Importe: 42 euros.'
        findings = engine.analyze(text=text, language='es', entities=['EMAIL_ADDRESS', 'PHONE_NUMBER'], score_threshold=0.35)
        if not {'EMAIL_ADDRESS', 'PHONE_NUMBER'} <= {r.entity_type for r in findings}:
            raise ValueError('No se detectaron el correo y el telefono sinteticos.')
        spans = resolve_spans(text, findings)
        output = render_identities(text, spans, default_assignments(text, spans))
        if 'prueba@example.com' in output or '612345678' in output or 'Importe: 42 euros.' not in output:
            raise ValueError('La sustitucion sintetica o la conservacion del importe fallo.')
    print('82 versiones correctas; modelo xx_ent_wiki_sm 3.8.0 cargado; prueba sintetica superada.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Error de verificacion: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
