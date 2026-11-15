"""Streamlit app for Presidio."""

import logging
import os
import re
import html
from pathlib import Path
from anonimizar_documents import LOCAL_OWNER, recent, load, save, rename_document as rename_history_document, move_to_trash
from anonimizar_local import read_settings, history_enabled, save_preferences, update_settings

import dotenv
import streamlit as st
from presidio_branding import apply_branding, motion_markup, hero_background, animate_placeholder
from identidades_ui import identity_review, sync_review

st.set_page_config(
    page_title="Inicio | Anonimizar",
    page_icon=os.path.join(os.path.dirname(__file__), "anonimizar-icon.svg"),
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "anonimizar — La aplicación procesa localmente y no envía automáticamente tus documentos a servicios externos.",
    },
)

# Apply the local anonimizar identity.
apply_branding()
from anonimizar_appearance import render_appearance, background_markup
st.markdown("<style>" + (Path(__file__).parent / "assets/appearance.css").read_text(encoding="utf-8") + "</style>", unsafe_allow_html=True)
st.markdown('<style>' + (Path(__file__).parent / 'workspace.css').read_text(encoding='utf-8') + '</style>', unsafe_allow_html=True)
st.markdown('<style>' + (Path(__file__).parent / 'product-ui.css').read_text(encoding='utf-8') + '</style>', unsafe_allow_html=True)

# Restore only local, non-sensitive preferences. Legacy auth flags are inert.
try:
    local_settings = read_settings()
    legacy_database = Path(__file__).parent / '.data/documents.sqlite3'
    if legacy_database.is_file() and not local_settings.get('legacy_database'):
        update_settings(legacy_database=str(legacy_database.resolve()))
except (OSError, ValueError):
    st.error('No se pudieron leer los ajustes locales. Conserva settings.json y revisa su formato o los permisos de la carpeta de datos.')
    st.stop()
if not st.session_state.get('anon_local_initialized'):
    for key in ('anon_auth_pending', 'anon_public_landing', 'anon_account', 'anon_pending_text', 'anon_preferences'):
        st.session_state.pop(key, None)
    st.session_state['anon_local_initialized'] = True
for key, value in local_settings.get('preferences', {}).items():
    if key not in st.session_state:
        st.session_state[key] = value
# Keep in-memory working values when the local settings page omits their widgets.
# This does not serialize drafts, word lists or encryption keys to disk.
for key in ('text_input', 'workspace_input', 'allow_list', 'deny_list', 'doc_encrypt_key'):
    if key in st.session_state:
        st.session_state[key] = st.session_state[key]

logger = logging.getLogger("presidio-streamlit")

MAX_TEXT_CHARS = 10_000


def submit_document():
    """Validate before switching screens; callbacks run before the layout is built."""
    st.session_state.pop('anon_settings_view', None)
    text = st.session_state.get('text_input', '')
    if not text.strip():
        st.session_state.pop('anon_input_error', None)
    elif len(text) > MAX_TEXT_CHARS:
        st.session_state['anon_input_error'] = 'Límite provisional: 10.000 caracteres. Reduce el texto para analizarlo; no se ha truncado ni procesado.'
    else:
        st.session_state.pop('anon_public_landing', None)
        st.session_state.pop('anon_input_error', None)
        st.session_state['anon_workspace'] = True
        st.session_state['anon_submitted_text'] = text
        st.session_state['anon_document_text'] = text
        st.session_state.pop('anon_skip_history_save', None)



def new_document():
    from identidades_ui import reset_review
    reset_review()
    st.session_state.pop('anon_mobile_history', None)
    st.session_state.pop('anon_document_id', None)
    st.session_state.pop('anon_restore_review', None)
    st.session_state.pop('anon_settings_view', None)
    st.session_state.pop('anon_workspace_tool', None)
    st.session_state['workspace_input'] = ''
    st.session_state['text_input'] = ''
    for key in ('anon_workspace', 'anon_submitted_text', 'anon_document_text', 'anon_input_error'):
        st.session_state.pop(key, None)


def open_document(document_id):
    payload = load(LOCAL_OWNER, document_id)
    if not payload:
        st.session_state['anon_input_error'] = 'Ese documento ya no está disponible. Comprueba la papelera en Configuración.'
        return
    from identidades_ui import reset_review
    reset_review()
    close_mobile_history()
    st.session_state['anon_document_id'] = document_id
    st.session_state['text_input'] = payload['text']
    st.session_state['anon_submitted_text'] = payload['text']
    st.session_state['anon_document_text'] = payload['text']
    st.session_state['anon_workspace'] = True
    st.session_state.pop('anon_settings_view', None)
    st.session_state.pop('anon_workspace_tool', None)
    st.session_state['anon_restore_review'] = payload.get('review', {})
    for key, value in payload.get('settings', {}).items():
        if key in ('doc_operator','doc_threshold','doc_explanations','doc_mask_count','doc_mask_char','doc_encrypt_key','doc_entities','allow_list','deny_list'):
            st.session_state[key] = value


def show_home():
    for key in ('anon_mobile_history', 'anon_workspace', 'anon_settings_view', 'anon_public_landing'):
        st.session_state.pop(key, None)


def close_mobile_history():
    st.session_state.pop('anon_mobile_history', None)


def show_mobile_history():
    close_search()
    st.session_state['anon_mobile_history'] = True


def close_search():
    st.session_state.pop('anon_search_open', None)


def show_settings():
    close_search()
    close_mobile_history()
    st.session_state['anon_settings_view'] = True


def open_workspace_tool(tool):
    close_search()
    if tool == 'original':
        st.session_state['original_edit_draft'] = st.session_state.get('anon_document_text', st.session_state.get('text_input', ''))
        st.session_state.pop('anon_input_error', None)
    st.session_state['anon_workspace_tool'] = tool


def cancel_original_edit():
    st.session_state['original_edit_draft'] = st.session_state.get('anon_document_text', st.session_state.get('text_input', ''))
    st.session_state.pop('anon_workspace_tool', None)
    st.session_state.pop('anon_input_error', None)


def send_original_edit():
    draft = st.session_state.get('original_edit_draft', '')
    if not draft.strip():
        return
    if len(draft) > MAX_TEXT_CHARS:
        st.session_state['anon_input_error'] = 'Límite provisional: 10.000 caracteres. Reduce el texto para analizarlo; no se ha truncado ni procesado.'
        return
    st.session_state['text_input'] = draft
    submit_document()
    st.session_state.pop('anon_workspace_tool', None)


def show_history_rename(document_id, title):
    st.session_state['history_rename_target'] = document_id
    st.session_state['history_rename_value'] = title


def close_history_rename():
    st.session_state.pop('history_rename_target', None)


@st.dialog('Cambiar nombre', on_dismiss=close_history_rename)
def history_rename_dialog():
    with st.container(key='history_rename_panel'):
        with st.form('history_rename_form'):
            title = st.text_input('Nombre del documento', key='history_rename_value', max_chars=120)
            left, right = st.columns([1, 1])
            cancelled = left.form_submit_button('Cancelar', width='stretch')
            submitted = right.form_submit_button('Guardar', type='primary', width='stretch')
        if cancelled:
            close_history_rename()
            st.rerun()
        if submitted:
            try:
                rename_history_document(st.session_state['history_rename_target'], title)
            except (ValueError, __import__('sqlite3').Error) as error:
                st.error(str(error) if isinstance(error, ValueError) else 'No se pudo cambiar el nombre. Vuelve a intentarlo.')
            else:
                close_history_rename()
                st.rerun()


def delete_history_document(document_id):
    try:
        move_to_trash(document_id)
    except __import__('sqlite3').Error:
        st.session_state['anon_input_error'] = 'No se pudo mover el documento a la papelera. Vuelve a intentarlo.'
        return
    if st.session_state.get('anon_document_id') == document_id:
        new_document()
        st.session_state['anon_skip_history_save'] = True


# A single local workspace; no authentication or public landing in the app.
rail = st.container(key='dashboard_rail')
logo = (Path(__file__).parent / 'anonimizar-icon.svg').read_text(encoding='utf-8')
rail.markdown('<div class="dashboard-logo">' + logo + '</div>', unsafe_allow_html=True)
rail.button('Anonimizar · Inicio', key='nav_home', on_click=show_home, help='Volver al texto sin borrar el borrador')
rail.button('Nuevo', key='nav_new', on_click=new_document, width='stretch')
with rail.container(key='nav_search'):
    st.text_input('Buscar documentos', key='rail_search_inline', placeholder='Buscar', label_visibility='collapsed')
rail.button('Configuración', key='nav_settings', on_click=show_settings, width='stretch')
rail.button('Cerrar historial', key='rail_history_close', on_click=close_mobile_history, icon=':material/close:')
with rail.container(key='document_history'):
    st.markdown('<div class="rail-label">Documentos</div>', unsafe_allow_html=True)
    rail_documents = recent(LOCAL_OWNER)
    for document in rail_documents:
        with st.container(key='history_row_' + document['id']):
            st.button(document['title'], key='rail_' + document['id'], on_click=open_document, args=(document['id'],), width='stretch', icon=':material/description:')
            with st.popover('Opciones de ' + document['title'], key='history_more_' + document['id'], icon=':material/more_horiz:'):
                st.button('Cambiar nombre', key='history_rename_' + document['id'], on_click=show_history_rename, args=(document['id'], document['title']), icon=':material/edit:')
                st.button('Eliminar', key='history_delete_' + document['id'], on_click=delete_history_document, args=(document['id'],), icon=':material/delete:')
    if not rail_documents:
        st.markdown('<div class="rail-empty">Aún no hay documentos</div>', unsafe_allow_html=True)
    if rail_documents:
        st.markdown('<div class="rail-search-empty" hidden>No hay documentos que coincidan.</div>', unsafe_allow_html=True)
# Keep the browser tab aligned with the active view, including early-stop pages.
if st.session_state.get('anon_settings_view'):
    browser_title = 'Configuración'
elif st.session_state.get('anon_workspace'):
    browser_title = 'Documento'
else:
    browser_title = 'Inicio'
st.set_page_config(page_title=f'{browser_title} | Anonimizar')
render_appearance(rail)
st.html('<script>' + (Path(__file__).parent / 'assets' / 'rail-search.js').read_text(encoding='utf-8') + '</script>', unsafe_allow_javascript=True)
st.html('<script>' + (Path(__file__).parent / 'assets' / 'composer-enter.js').read_text(encoding='utf-8') + '</script>', unsafe_allow_javascript=True)
mobile_nav = st.container(key='mobile_navigation')
mobile_nav.button('Inicio', key='mobile_home', on_click=show_home)
mobile_nav.button('Documentos', key='mobile_documents', on_click=show_mobile_history)
mobile_nav.button('Configuración', key='mobile_settings', on_click=show_settings)
st.markdown('<div class="dashboard-marker' + (' mobile-history-open' if st.session_state.get('anon_mobile_history') else '') + '"></div>', unsafe_allow_html=True)
detector_settings = None
if st.session_state.get('history_rename_target'):
    history_rename_dialog()
if st.session_state.get('anon_settings_view') == 'detector':
    from anonimizar_local_ui import render_local_settings
    detector_settings = render_local_settings(show_home, detector=True)
elif st.session_state.get('anon_settings_view') is True:
    from anonimizar_local_ui import render_local_settings
    render_local_settings(show_home)
    st.stop()
workspace = st.session_state.get('anon_workspace', False) or st.session_state.get('anon_settings_view', False)
chat_workspace = workspace and not st.session_state.get('anon_settings_view', False)
if chat_workspace:
    st.session_state['text_input'] = st.session_state.get('anon_document_text', st.session_state.get('anon_submitted_text', st.session_state.get('text_input', '')))
    from anonimizar_workspace import original_message, result_message, result_toolbar, reference_icon_css
    st.markdown(reference_icon_css(), unsafe_allow_html=True)
    tool = st.session_state.get('anon_workspace_tool', '')
    st.markdown('<div class="chat-workspace workspace-tool-' + tool + '"></div>', unsafe_allow_html=True)
    header = st.container(key='chat_header')
    header.button('Cerrar documento', key='chat_mobile_close', on_click=show_home, icon=':material/close:')
    with header.popover('Documento anonimizado', key='chat_document_menu'):
        st.button('Nuevo texto', key='chat_new_document', on_click=new_document)
        st.button('Volver al inicio', key='chat_home', on_click=show_home)
        st.button('Configuración del documento', key='chat_document_settings', on_click=open_workspace_tool, args=('settings',))
    header.button('Salir de pantalla completa' if st.session_state.get('chat_expanded') else 'Ampliar conversación', key='chat_fullscreen', on_click=lambda: st.session_state.update(chat_expanded=not st.session_state.get('chat_expanded', False)), icon=':material/fullscreen:')
    if st.session_state.get('chat_expanded'):
        st.markdown('<div class="chat-expanded"></div>', unsafe_allow_html=True)
    conversation = st.container(key='chat_conversation')
    comparison_shell = conversation.container(key='comparison_shell')
    comparison_shell.markdown(original_message(st.session_state.get('text_input', '')), unsafe_allow_html=True)
    original_editor = comparison_shell.container(key='original_editor')
    composer = original_editor
    output_column = comparison_shell.container(key='assistant_message')
elif workspace:
    header = st.container(key='workspace_header')
    header.title('Configuración' if st.session_state.get('anon_settings_view') else 'Revisa tu documento')
    header.button('Nuevo texto', on_click=new_document)

    comparison_shell = st.container(key='comparison_shell')
    input_column, output_column = comparison_shell.columns(2, gap='large')
    input_column.subheader('Original')
    composer = input_column
else:
    hero = st.container(key="entry_hero")
    hero.markdown(background_markup(), unsafe_allow_html=True)
    hero.markdown('<div class="dashboard-pill"><span class="pill-icons" aria-hidden="true"><span class="pill-track"><span>C</span><span>D</span><span>A</span><span>M</span></span></span>+10.000 Usuarios</div>', unsafe_allow_html=True)
    hero.markdown('<div class="anon-hero-heading"><h1>¿Qué anonimizamos?</h1></div>', unsafe_allow_html=True)
    composer = hero
input_panel = composer.container(key="input_panel")
input_container = input_panel.container(key="input_preview")
input_footer = input_panel.container(key="input_footer")


# The requested action is explicit; editing invalidates the previous result.
if 'text_input' not in st.session_state:
    st.session_state['text_input'] = ''
if chat_workspace:
    st_text = st.session_state['text_input']
    if 'original_edit_draft' not in st.session_state:
        st.session_state['original_edit_draft'] = st_text
    input_container.text_area('Editar mensaje original', key='original_edit_draft', label_visibility='collapsed', height=68)
    input_footer.button('Cancelar', key='original_edit_cancel', on_click=cancel_original_edit)
    submit_anonymization = input_footer.button('Enviar', key='anonymize_document', on_click=send_original_edit, type='primary')
else:
    st_text = input_container.text_area(
        label="Texto para anonimizar", height=68, key="text_input", label_visibility="collapsed",
        placeholder="Pega el texto que quieres anonimizar…",
    )
    input_footer.markdown('<div class="anon-composer-tools"><button type="button" class="anon-add" aria-label="Acciones adicionales" aria-haspopup="dialog" aria-expanded="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v16M4 12h16"/></svg></button><button type="button" class="anon-input-mode" aria-haspopup="dialog" aria-expanded="false"><span>Anonimizar</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m7 10 5 5 5-5"/></svg></button><button type="button" class="anon-voice" aria-label="Entrada de voz no disponible" title="Entrada de voz no disponible" disabled><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M6 11v1a6 6 0 0 0 12 0v-1M12 18v3m-3 0h6"/></svg></button></div>', unsafe_allow_html=True)
    submit_anonymization = input_footer.button('Enviar', key='anonymize_document', on_click=submit_document, type='primary', width='content', icon=':material/chevron_right:') and bool(st_text.strip())
if not chat_workspace:
    with open(os.path.join(os.path.dirname(__file__), 'assets', 'composer-controls.js'), encoding='utf-8-sig') as controls_source:
        st.html('<script>' + controls_source.read() + '</script>', unsafe_allow_javascript=True)
else:
    # Native callbacks for the response menu; no duplicate controls above input.
    quick_actions = st.container(key='chat_action_bridge')
    for label, name in [('Revisar personas', 'review'), ('Datos detectados', 'findings'), ('Configuración', 'settings'), ('Editar original', 'original')]:
        quick_actions.button(label, key='chat_tool_' + name, on_click=open_workspace_tool, args=(name,))
    with open(Path(__file__).parent / 'assets' / 'workspace-controls.js', encoding='utf-8') as controls_source:
        st.html('<script>' + controls_source.read() + '</script>', unsafe_allow_javascript=True)
if not workspace:
    animate_placeholder()
if st.session_state.get('anon_input_error'):
    input_panel.error(st.session_state['anon_input_error'])
if not workspace:
    st.stop()

# Load the local detection stack only after the user submits a document.
import pandas as pd
from annotated_text.util import get_annotated_html
from presidio_analyzer_config import config_path_for
from presidio_helpers import analyze, analyzer_engine, annotate, anonymize, get_supported_entities

if not chat_workspace:
    output_column.subheader("Anonimizado")
output_panel = output_column.container(key="output_panel")
motion_slot = output_panel.empty()
output_container = output_panel.container(key="output_preview")
details = st.container(key='chat_details') if chat_workspace else st.container()
if chat_workspace:
    details.button('Cerrar panel', key='chat_close_details', on_click=open_workspace_tool, args=('',), icon=':material/close:')
review_container = details.container(key="identity_review")
settings_container = detector_settings if detector_settings is not None else details.container(key="settings_panel")
if st.session_state.get("anon_settings_view"):
    st.markdown("<style>.st-key-comparison_shell,.st-key-identity_review,.st-key-findings_panel {display:none}</style>", unsafe_allow_html=True)
findings_container = details.container(key="findings_panel")
about_container = details.container(key="about_panel")
has_active_document = st.session_state.get('anon_submitted_text') == st_text
if not has_active_document:
    from identidades_ui import reset_review
    reset_review()
    st.session_state.pop('anon_submitted_text', None)
    motion_slot.markdown(motion_markup('idle'), unsafe_allow_html=True)
    output_container.info('Envía el texto actualizado para ver el resultado.')
else:
    motion_slot.markdown(motion_markup('loading'), unsafe_allow_html=True)


def parse_word_list(raw: str) -> list:
    """Split a free-text allow/deny list (newline- or comma-separated) into words."""
    return [word.strip() for word in re.split(r"[,\n]", raw or "") if word.strip()]


# Configuration remains available below the comparison.
if detector_settings is None:
    settings_container.header("Configuración")


model_help_text = """
    Select which Named Entity Recognition (NER) model to use for PII detection, in parallel to rule-based recognizers.
    """

model_list = ["spaCy/xx_ent_wiki_sm"]
# Select model
st_model = settings_container.selectbox(
    "Modelo de detección",
    model_list,
    index=0,
    help=model_help_text,
)

# Extract model package.
st_model_package = st_model.split("/")[0]

# Remove package prefix (if needed)
st_model = (
    st_model
    if st_model_package.lower() not in ("spacy", "stanza", "huggingface", "gliner")
    else "/".join(st_model.split("/")[1:])
)

settings_container.caption("Modelo instalado localmente; esta copia no requiere descargarlo durante el uso.")

settings_container.caption(
    "Prueba local en español · spaCy xx_ent_wiki_sm. Revisión humana necesaria."
)

analyzer_params = (st_model_package, st_model)
logger.debug(f"analyzer_params: {analyzer_params}")

st_operator = settings_container.selectbox(
    "Modo de anonimización",
    ["redact", "replace", "highlight", "mask", "hash", "encrypt"], key="doc_operator",
    format_func=lambda mode: {"redact":"Eliminar", "replace":"Sustituir", "highlight":"Resaltar", "mask":"Ocultar", "hash":"Huella digital", "encrypt":"Cifrar"}[mode],
    index=1,
    help="""
    Select which manipulation to the text is requested after PII has been identified.\n
    - Redact: Completely remove the PII text\n
    - Replace: Replace the PII text with a constant, e.g. <PERSON>\n
    - Highlight: Shows the original text with PII highlighted in colors\n
    - Mask: Replaces a requested number of characters with an asterisk (or other mask character)\n
    - Hash: Replaces with the hash of the PII string\n
    - Encrypt: Replaces with an AES encryption of the PII string, allowing the process to be reversed
         """,
)
st_mask_char = "*"
st_number_of_chars = 15
st_encrypt_key = "WmZq4t7w!z%C&F)J"


logger.debug(f"st_operator: {st_operator}")


if st_operator == "mask":
    st_number_of_chars = settings_container.number_input(
        "Número de caracteres", key="doc_mask_count", value=st_number_of_chars, min_value=0, max_value=100
    )
    st_mask_char = settings_container.text_input(
        "Carácter para ocultar", key="doc_mask_char", value=st_mask_char, max_chars=1
    )
elif st_operator == "encrypt":
    st_encrypt_key = settings_container.text_input("Clave de cifrado", key="doc_encrypt_key", value=st_encrypt_key)
st_threshold = settings_container.slider(
    label="Sensibilidad de detección", key="doc_threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.35,
    help="Define the threshold for accepting a detection as PII. See more here: ",
)

st_return_decision_process = settings_container.checkbox(
    "Mostrar explicaciones de los datos detectados", key="doc_explanations",
    value=False,
    help="Add the decision process to the output table. "
    "Shows how each finding was identified.",
)

# Allow and deny lists
st_deny_allow_expander = settings_container.expander(
    "Palabras que conservar u ocultar",
    expanded=False,
)

with st_deny_allow_expander:
    st_allow_list = parse_word_list(
        st.text_area(
            label="Palabras que conservar",
            help="One word per line (or comma-separated).",
            key="allow_list",
        )
    )
    st.caption(
        "Allowlists contain words that are not considered PII, but are detected as such."
    )

    st_deny_list = parse_word_list(
        st.text_area(
            label="Palabras que ocultar",
            help="One word per line (or comma-separated).",
            key="deny_list",
        )
    )
    st.caption(
        "Denylists contain words that are considered PII, but are not detected as such."
    )
# Main panel

with about_container.expander("Acerca de anonimizar", expanded=False):
    st.info(
        "anonimizar. La aplicación procesa localmente y no envía automáticamente tus documentos a servicios externos."
    )
    st.info(
        "Pega el texto, revisa los datos detectados, corrige las personas y comprueba el resultado antes de copiar. "
        "Revisión humana necesaria; los domicilios y las descripciones indirectas pueden seguir identificando a alguien."
    )
    st.caption('Las licencias y atribuciones de terceros se conservan en la documentación incluida.')

# Model configuration (YAML) — read-only by default; editable when ALLOW_CONFIG_EDIT is set.
# The value is resolved here (from session state); the viewer/editor itself is rendered
# lower, between the text panels and the findings table (see ``config_container``).
allow_config_edit = os.getenv("ALLOW_CONFIG_EDIT", "").lower() in ("1", "true", "yes")
st_config_yaml = None
config_text = None
config_path = None
config_editor_key = f"config_yaml_editor::{st_model_package}/{st_model}"
try:
    config_path = config_path_for(st_model_package, st_model)
    with open(config_path) as config_file:
        config_text = config_file.read()
    # If the user has edited this model's YAML in the editor below, build from it.
    if allow_config_edit:
        current_yaml = st.session_state.get(config_editor_key, config_text)
        if current_yaml.strip() != config_text.strip():
            st_config_yaml = current_yaml
except Exception as config_err:
    logger.warning(f"Could not load YAML config: {config_err}")

analyzer_load_state = st.info("Iniciando anonimizar...")

analyzer_load_state.empty()

if len(st_text) > MAX_TEXT_CHARS:
    from identidades_ui import reset_review
    reset_review()
    st.session_state.pop('anon_submitted_text', None)
    motion_slot.markdown(motion_markup('idle'), unsafe_allow_html=True)
    st.error('Límite provisional: 10.000 caracteres. Reduce el texto para analizarlo; no se ha truncado ni procesado.')
    st.stop()

# Reserved slot for the model-configuration YAML, shown between the text panels
# above and the findings table below. Filled after analysis so it always renders
# (even if an invalid edit makes analysis error, the editor stays available to fix).
config_container = settings_container.container()

try:
    # Choose entities
    st_entities_expander = settings_container.expander("Tipos de datos que detectar")
    st_entities = st_entities_expander.multiselect(
        label="Selecciona los tipos de datos", key="doc_entities",
        options=get_supported_entities(*analyzer_params, config_yaml=st_config_yaml),
        default=list(
            get_supported_entities(*analyzer_params, config_yaml=st_config_yaml)
        ),
        help="Limit the list of PII entities detected. "
        "This list is dynamic and based on the NER model and registered recognizers. "
        "Choose the entity types included in detection.",
    )

    try:
        save_preferences(st.session_state)
    except (OSError, ValueError):
        settings_container.warning('Los ajustes funcionan en esta sesión, pero no se pudieron guardar en el equipo.')

    # Keep configuration accessible before the first request. Never process an
    # edited document or expose a stale output until Anonimizar is pressed.
    if not has_active_document or detector_settings is not None:
        if config_text is not None:
            with config_container.expander("Configuración avanzada del modelo", expanded=False):
                st.caption("This NER setup is loaded declaratively via "
                           f"`AnalyzerEngineProvider` from `config/{os.path.basename(config_path)}`.")
                if allow_config_edit:
                    st.text_area("Edit the configuration — the analyzer rebuilds from this YAML:",
                                 value=config_text, height=400, key=config_editor_key)
                else:
                    st.code(config_text, language="yaml")
                    st.caption("Set `ALLOW_CONFIG_EDIT=true` to edit this configuration in-app.")
        st.stop()

    # Before
    analyzer_load_state = st.info("Iniciando anonimizar...")
    analyzer = analyzer_engine(*analyzer_params, config_yaml=st_config_yaml)
    analyzer_load_state.empty()

    st_analyze_results = analyze(
        *analyzer_params,
        config_yaml=st_config_yaml,
        text=st_text,
        entities=st_entities,
        language="es",
        score_threshold=st_threshold,
        return_decision_process=st_return_decision_process,
        allow_list=st_allow_list,
        deny_list=st_deny_list,
    )

    sync_review(st_text, st_analyze_results, {
        'operator': st_operator, 'threshold': st_threshold, 'entities': st_entities,
        'allow': st_allow_list, 'deny': st_deny_list, 'config': st_config_yaml,
        'mask': [st_mask_char, st_number_of_chars],
    })
    if st.session_state.get('anon_restore_review') is not None:
        for key, value in st.session_state.pop('anon_restore_review').items():
            if key == 'identity_manual':
                value = [tuple(span) for span in value]
            if key in ('identity_scope', 'identity_manual', 'identity_confirmed') or key.startswith('identity_assignment_'):
                st.session_state[key] = value
    # After
    if st_operator != "highlight":
        with output_panel:
            if st_operator == 'replace':
                with review_container:
                    output_text = identity_review(st_text, st_analyze_results)
            else:
                st.warning('Este modo no conserva las etiquetas de persona revisadas. Usa replace para distinguir participantes.')
                st_anonymize_results = anonymize(
                text=st_text,
                operator=st_operator,
                mask_char=st_mask_char,
                number_of_chars=st_number_of_chars,
                encrypt_key=st_encrypt_key,
                analyze_results=st_analyze_results,
                )
                output_text = st_anonymize_results.text
            with output_container:
                if chat_workspace:
                    st.markdown(result_message(output_text), unsafe_allow_html=True)
                else:
                    st.code(output_text, language=None, wrap_lines=True, height="stretch")
    else:
        annotated_tokens = annotate(text=st_text, analyze_results=st_analyze_results)
        with output_container:
            st.markdown('<div class="anon-highlighted-text">' + get_annotated_html(*annotated_tokens) + '</div>', unsafe_allow_html=True)
            if chat_workspace:
                st.markdown('<span class="chat-highlight-source" hidden>' + html.escape(st_text) + '</span>', unsafe_allow_html=True)
    if chat_workspace:
        output_container.markdown(result_toolbar(), unsafe_allow_html=True)
        output_container.button('Anonimizar otro texto', key='result_restart', on_click=new_document, icon=':material/add:')

    # Persist only with explicit local history opt-in.
    if has_active_document and history_enabled() and not st.session_state.get('anon_skip_history_save'):
        payload = {'text': st_text, 'settings': {key: st.session_state[key] for key in ('doc_operator','doc_threshold','doc_explanations','doc_mask_count','doc_mask_char','doc_encrypt_key','doc_entities','allow_list','deny_list') if key in st.session_state},
                   'review': {key: value for key, value in st.session_state.items() if key in ('identity_scope', 'identity_manual', 'identity_confirmed') or key.startswith('identity_assignment_')}}
        try:
            st.session_state['anon_document_id'] = save(LOCAL_OWNER, payload, st.session_state.get('anon_document_id'))
        except (OSError, __import__('sqlite3').Error):
            st.warning('El resultado está disponible, pero no se pudo guardar en el historial local. Comprueba el espacio libre y los permisos en Configuración.')

    if has_active_document and not history_enabled():
        output_container.caption('Historial desactivado: este texto no se guardará automáticamente.')
        if output_container.button('Activar historial y guardar este documento', key='enable_history_result'):
            update_settings(history_enabled=True)
            st.session_state.pop('anon_skip_history_save', None)
            st.rerun()

    # Emit completion only after the real result is available. The last frame
    # dissolves over the result; no timer delays analysis or invents progress.
    motion_slot.markdown(motion_markup('complete' if submit_anonymization else 'ready'), unsafe_allow_html=True)

    with findings_container:
        # table result
        st.subheader(
            "Datos detectados"
            if not st_return_decision_process
            else "Datos detectados y sus explicaciones"
        )
        st.caption('Esta tabla contiene datos originales. Su descarga CSV no es el resultado revisado para compartir.')
        if st_analyze_results:
            df = pd.DataFrame.from_records([r.to_dict() for r in st_analyze_results])
            df["text"] = [st_text[res.start : res.end] for res in st_analyze_results]

            df_subset = df[["entity_type", "text", "start", "end", "score"]].rename(
                {
                    "entity_type": "Entity type",
                    "text": "Text",
                    "start": "Start",
                    "end": "End",
                    "score": "Confidence",
                },
                axis=1,
            )
            df_subset["Text"] = [st_text[res.start : res.end] for res in st_analyze_results]
            if st_return_decision_process:
                analysis_explanation_df = pd.DataFrame.from_records(
                    [r.analysis_explanation.to_dict() for r in st_analyze_results]
                )
                df_subset = pd.concat([df_subset, analysis_explanation_df], axis=1)
            st.dataframe(df_subset.reset_index(drop=True), width="stretch")
        else:
            st.text("No se han detectado datos personales")


except Exception as e:
    st.session_state.pop('anon_submitted_text', None)
    motion_slot.markdown(motion_markup('error'), unsafe_allow_html=True)
    logger.error('No se pudo procesar el texto; detalle omitido para evitar registrar contenido.')
    output_container.error('No se pudo procesar el texto. Revisa la configuración y vuelve a intentarlo con un ejemplo ficticio.')

# Render the model-configuration YAML into the slot reserved above (between the
# text panels and the findings table).
with config_container:
    if config_text is not None and config_path is not None:
        with st.expander("Configuración avanzada del modelo", expanded=False):
            st.caption(
                "This NER setup is loaded declaratively via "
                f"`AnalyzerEngineProvider` from `config/{os.path.basename(config_path)}`."
            )
            if allow_config_edit:
                st.text_area(
                    "Edit the configuration — the analyzer rebuilds from this YAML:",
                    value=config_text,
                    height=400,
                    key=config_editor_key,
                )
            else:
                st.code(config_text, language="yaml")
                st.caption(
                    "Set `ALLOW_CONFIG_EDIT=true` to edit this configuration in-app."
                )


