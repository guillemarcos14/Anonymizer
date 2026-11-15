"""Identidades revisables dentro de un texto. Sin persistencia ni inferencia de alias."""
import re
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


def mention_key(span):
    return f"{span['start']}:{span['end']}"


def resolve_spans(text, findings, manual=()):
    """Usa la resolución de solapamientos del motor, sin fusionar vecinos por espacios."""
    result = AnonymizerEngine().anonymize(
        text=text, analyzer_results=findings,
        operators={'DEFAULT': OperatorConfig('custom', {'lambda': lambda value: value})},
        merge_entities_with_spaces=False,
    )
    spans = sorted([{'start': i.start, 'end': i.end, 'entity_type': i.entity_type}
                    for i in result.items], key=lambda s: (s['start'], s['end']))
    for start, end in manual:
        if not (isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(text)):
            raise ValueError('La mención añadida no corresponde al texto actual.')
        overlapping = [s for s in spans if s['start'] < end and s['end'] > start]
        if any(s['start'] == start and s['end'] == end and s['entity_type'] == 'PERSON' for s in overlapping):
            continue
        if overlapping:
            raise ValueError('El nombre añadido se solapa con otra detección. Corrige primero sus límites.')
        spans.append({'start': start, 'end': end, 'entity_type': 'PERSON'})
    spans.sort(key=lambda s: (s['start'], s['end']))
    if any(a['end'] > b['start'] for a, b in zip(spans, spans[1:])):
        raise ValueError('Hay detecciones solapadas. Revisa sus límites antes de continuar.')
    return spans


def literal_mentions(text, name):
    if not name or not name.strip():
        raise ValueError('Escribe el nombre tal como aparece en el texto.')
    # Evita convertir Luisana en [Persona N]ana al añadir Luis.
    matches = [(m.start(), m.end()) for m in re.finditer(r'(?<!\w)' + re.escape(name) + r'(?!\w)', text)]
    if not matches:
        raise ValueError('Ese nombre no aparece exactamente en el texto. Cópialo del original.')
    return matches


def default_assignments(text, spans):
    groups, assignments = {}, {}
    for span in spans:
        if span['entity_type'] == 'PERSON':
            name = text[span['start']:span['end']]
            groups.setdefault(name, len(groups) + 1)
            assignments[mention_key(span)] = groups[name]
    return assignments


def render_identities(text, spans, assignments):
    """Reemplaza spans confirmables; conserva literalmente todo el texto intermedio."""
    if re.search(r'\[Persona [1-9][0-9]*\]', text):
        raise ValueError('El original ya contiene etiquetas [Persona número]. Renómbralas antes de continuar para evitar confusiones.')
    people = [s for s in spans if s['entity_type'] == 'PERSON']
    if set(assignments) != {mention_key(s) for s in people}:
        raise ValueError('Las asignaciones no corresponden a las menciones actuales. Reinicia la revisión.')
    if any(type(v) is not int or not 1 <= v <= len(people) for v in assignments.values()):
        raise ValueError('Selecciona una persona válida para cada mención.')
    parts, cursor = [], 0
    for span in spans:
        start, end = span['start'], span['end']
        if not 0 <= cursor <= start < end <= len(text):
            raise ValueError('Los límites de las detecciones no son válidos.')
        parts.append(text[cursor:start])
        parts.append(f"[Persona {assignments[mention_key(span)]}]" if span['entity_type'] == 'PERSON'
                     else f"<{span['entity_type']}>")
        cursor = end
    parts.append(text[cursor:])
    return ''.join(parts)
