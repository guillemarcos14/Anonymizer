"""Local settings and data controls for the installed application."""
import json
import sqlite3
from pathlib import Path
import streamlit as st
from anonimizar_local import VERSION, data_dir, read_settings, update_settings
from anonimizar_documents import (LOCAL_OWNER, database_path, recent, export_history,
    import_history, move_to_trash, restore_trash, trash_count, purge_trash,
    legacy_sources, legacy_path, migrate_legacy)


def _select_settings(section):
    st.session_state['local_settings_section'] = section
    st.session_state['anon_settings_view'] = True


def render_local_settings(show_home, detector=False):
    section = 'anonymization' if detector else st.session_state.get('local_settings_section', 'history')
    with st.container(key='local_settings'):
        with st.container(key='settings_nav'):
            st.markdown('<p class="settings-nav-heading">Configuración</p>', unsafe_allow_html=True)
            for value, label, icon in [('history', 'Historial', ':material/history:'), ('anonymization', 'Anonimización', ':material/tune:'), ('application', 'Aplicación local', ':material/desktop_windows:')]:
                st.button(label, key='settings_nav_' + value, icon=icon, type='primary' if section == value else 'secondary', on_click=_select_settings, args=(value,), width='stretch')
            st.button('Volver al texto', key='settings_back', icon=':material/arrow_back:', on_click=show_home, width='stretch')
        st.button('Cerrar configuración', key='settings_close', icon=':material/close:', on_click=show_home)
        with st.container(key='settings_content'):
            if section == 'history':
                st.markdown('<header class="settings-section-heading"><h2>Historial en este equipo</h2><p>Controla qué guardas y gestiona tus documentos.</p></header>', unsafe_allow_html=True)
                _history_settings()
            elif section == 'anonymization':
                if detector:
                    st.markdown('<div class="settings-detector-marker"></div>', unsafe_allow_html=True)
                    st.markdown('<header class="settings-section-heading"><h2>Detección y anonimización</h2><p>Ajusta cómo se reconocen y protegen los datos de tus textos.</p></header>', unsafe_allow_html=True)
                    st.button('Volver a Anonimización', key='settings_detector_back', icon=':material/arrow_back:', on_click=_select_settings, args=('anonymization',))
                    return st.container(key='settings_detector_panel')
                st.markdown('<header class="settings-section-heading"><h2>Anonimización</h2><p>Configura cómo se detectan y protegen los datos personales.</p></header>', unsafe_allow_html=True)
                with st.container(key='settings_detection_panel'):
                    left, right = st.columns([3, 1], vertical_alignment='center')
                    with left:
                        st.markdown('**Detección y modo de anonimización**')
                        st.caption('Ajusta los tipos de datos, las reglas y el modo de protección del texto.')
                    with right:
                        if st.button('Gestionar', key='settings_manage_detection'):
                            st.session_state['anon_settings_view'] = 'detector'
                            st.rerun()
            else:
                st.markdown('<header class="settings-section-heading"><h2>Aplicación local</h2><p>Información, almacenamiento y mantenimiento de Anonimizar.</p></header>', unsafe_allow_html=True)
                with st.container(key='settings_application_panel'):
                    _application_settings()


def _history_settings():
    with st.container(key="settings_history_panel"):
        with st.container(key="settings_history_row"):
            left, right = st.columns([5, 1], vertical_alignment='center')
            with left:
                st.markdown('**Guardar los próximos documentos**')
                st.caption('Conserva originales, ajustes y revisión en este usuario de Windows. Puedes anonimizar sin guardar textos.')
            with right:
                st.toggle('Guardar los próximos documentos', value=read_settings().get('history_enabled', True), label_visibility='collapsed',
                          key='local_history_toggle', on_change=lambda: update_settings(history_enabled=st.session_state['local_history_toggle']))
        st.caption('Desactivarlo detiene el guardado automático; no borra lo que ya conservaste.')
        with st.container(key="settings_location_row"):
            st.markdown('**Ubicación del historial**')
            st.code(str(database_path()), language=None)
    with st.container(key="settings_documents_panel"):
        documents = recent(LOCAL_OWNER)
        left, right = st.columns([3, 1], vertical_alignment='center')
        with left:
            st.markdown('**Copia del historial**')
            st.caption(f'{len(documents)} documentos guardados. La exportación incluye textos originales y ajustes; guárdala en un lugar de confianza.')
        with right:
            st.download_button('Exportar historial', export_history(), file_name='anonimizar-historial.json', mime='application/json', disabled=not documents)
        with st.expander('Restaurar una copia del historial'):
            uploaded = st.file_uploader('Copia JSON de Anonimizar', type=['json'])
            if st.button('Importar copia', disabled=uploaded is None):
                try:
                    count = import_history(uploaded.getvalue())
                    st.success(f'Copia importada: {count} documentos leídos. Los ya importados no se duplican.')
                except (ValueError, KeyError, TypeError, UnicodeError, sqlite3.Error):
                    st.error('No se pudo importar. Selecciona una exportación JSON válida de Anonimizar; no se ha eliminado el historial existente.')
        if documents:
            choices = {'Todos los documentos': None, **{f"{d['title']} · {d['id'][:6]}": d['id'] for d in documents}}
            selected = st.selectbox('Qué retirar del historial', list(choices))
            if st.button('Mover a la papelera'):
                move_to_trash(choices[selected])
                st.session_state.pop('anon_document_id', None)
                st.session_state['anon_skip_history_save'] = True
                st.rerun()
        count = trash_count()
        if count:
            st.caption(f'Papelera: {count} documentos. Puedes recuperarlos mientras no la vacíes.')
            if st.button('Restaurar papelera'):
                restore_trash()
                st.rerun()
            confirmed = st.checkbox('Confirmo que quiero borrar definitivamente los documentos de la papelera')
            if st.button('Vaciar papelera definitivamente', disabled=not confirmed):
                purge_trash()
                st.rerun()
        try:
            sources = legacy_sources()
        except (OSError, sqlite3.Error):
            sources = []
            st.warning('No se pudo leer el historial anterior. La base original se conserva sin cambios.')
        with st.expander('Recuperar documentos de la versión con cuentas'):
            source_path = st.text_input('Ruta de la base de documentos anterior', value=str(legacy_path()))
            if st.button('Leer colecciones de esta base'):
                candidate = Path(source_path)
                try:
                    if not candidate.is_file() or candidate.read_bytes()[:16] != b'SQLite format 3\x00':
                        raise ValueError('Base no válida')
                    update_settings(legacy_database=str(candidate.resolve()))
                    st.rerun()
                except (OSError, ValueError):
                    st.error('No se pudo abrir esa base. Selecciona el archivo documents.sqlite3 de la versión anterior.')
            if sources:
                st.write('Se copia solo la colección que elijas. Las bases originales se conservan y no se modifican.')
                selected = st.selectbox('Colección anterior', range(len(sources)), format_func=lambda i: f'Colección {i + 1} · {sources[i][1]} documentos')
                st.caption('Identificador de origen: ' + sources[selected][0])
                if st.button('Copiar esta colección al historial local'):
                    try:
                        count = migrate_legacy(sources[selected][0])
                        st.success(f'{count} documentos recuperados. La copia original permanece intacta.')
                    except (OSError, sqlite3.Error, ValueError):
                        st.error('No se pudo copiar la colección. Conserva la base anterior y comprueba el espacio libre y los permisos.')


def _application_settings():
    st.write(f'Anonimizar {VERSION} · Windows x64')
    st.caption('El motor funciona sin conexión. No hay registro, sincronización ni envío de documentos a servicios externos. Los archivos locales no están cifrados por la aplicación.')
    st.write('Actualizaciones: ejecuta el nuevo instalador de Anonimizar. Instala el programa por separado y conserva el historial y tus ajustes. No se descargan ni instalan actualizaciones en segundo plano.')
    st.code(str(data_dir()), language=None)
    runtime = data_dir() / 'runtime.json'
    if runtime.exists():
        if st.button('Cerrar Anonimizar y detener el motor'):
            try:
                state = json.loads(runtime.read_text(encoding='utf-8'))
                (data_dir() / 'stop.json').write_text(json.dumps({'token': state['token']}), encoding='utf-8')
                st.success('Cerrando el motor local. Puedes cerrar esta pestaña.')
            except (OSError, ValueError, KeyError):
                st.error('No se pudo solicitar el cierre. Cierra Anonimizar desde su lanzador.')
    else:
        st.caption('Sesión de desarrollo: el motor se detiene desde el proceso que lo inició.')
