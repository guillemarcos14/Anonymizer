"""Controles Streamlit de revisión; estado limitado a la entrada/configuración actual."""
import hashlib
import json
import streamlit as st
from identidades import (default_assignments, literal_mentions, mention_key,
                         render_identities, resolve_spans)


def clear_confirmation():
    st.session_state['identity_confirmed'] = False


def reset_assignments():
    for key in list(st.session_state):
        if key.startswith('identity_assignment_'):
            del st.session_state[key]
    clear_confirmation()


def reset_review():
    for key in list(st.session_state):
        if key.startswith('identity_'):
            del st.session_state[key]


def sync_review(text, findings, context):
    signature = hashlib.sha256(json.dumps(
        [text, [(r.start, r.end, r.entity_type, r.score) for r in findings], context],
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
    if st.session_state.get('identity_scope') != signature:
        reset_review()
        st.session_state['identity_scope'] = signature
        st.session_state['identity_manual'] = []
    return signature


def identity_review(text, findings):
    st.subheader('Revisar personas')
    st.caption('Los nombres idénticos comparten etiqueta inicialmente. Comprueba homónimos y abreviaturas: '
               'elige la misma persona para unir menciones o una distinta para separarlas. Solo se aplica a este texto.')
    st.caption('Añadir o quitar nombres reinicia la agrupación: hazlo antes de asignar las personas.')
    with st.expander('Añadir un nombre no detectado'):
        with st.form('identity_add_form', clear_on_submit=True):
            name = st.text_input('Nombre exacto que falta', key='identity_new_name')
            add = st.form_submit_button('Añadir sus apariciones')
        if add:
            try:
                manual = list(st.session_state.get('identity_manual', []))
                manual.extend(literal_mentions(text, name))
                resolve_spans(text, findings, manual)
                st.session_state['identity_manual'] = sorted(set(manual))
                reset_assignments()
            except ValueError as error:
                clear_confirmation()
                st.error(str(error))
        if st.session_state.get('identity_manual'):
            if st.button('Quitar menciones añadidas', key='identity_clear_manual'):
                st.session_state['identity_manual'] = []
                reset_assignments()
    st.button('Restablecer agrupación inicial', key='identity_reset_assignments', on_click=reset_assignments)
    spans = resolve_spans(text, findings, st.session_state.get('identity_manual', []))
    people = [s for s in spans if s['entity_type'] == 'PERSON']
    defaults = default_assignments(text, spans)
    assignments = {}
    for index, span in enumerate(people, 1):
        key = mention_key(span)
        name = text[span['start']:span['end']]
        left = max(0, span['start'] - 48)
        right = min(len(text), span['end'] + 64)
        st.caption(f"Mención {index}: {text[left:span['start']]}【{name}】{text[span['end']:right]}")
        assignments[key] = st.selectbox(
            f'Persona de la mención {index}: {name}', options=list(range(1, len(people) + 1)),
            index=defaults[key] - 1, format_func=lambda value: f'Persona {value}',
            key=f'identity_assignment_{key}', on_change=clear_confirmation,
        )
    output = render_identities(text, spans, assignments)
    if people:
        st.write('Comprueba todas las menciones, las personas distintas y los nombres que faltan antes de confirmar.')
        confirmed = st.checkbox(
            'Confirmo la revisión',
            key='identity_confirmed',
        )
        if confirmed:
            st.success('Identidades revisadas. Revisa también los demás datos y el contexto antes de copiar.')
        else:
            st.warning('Salida provisional: faltan confirmar las identidades. Revisa las menciones antes de copiar.')
    else:
        st.info('No hay personas marcadas. Revisa el original y añade los nombres que falten.')
    return output
