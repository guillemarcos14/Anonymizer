"""Offline appearance backgrounds captured from the pinned live reference."""
from pathlib import Path
import streamlit as st
from anonimizar_local import read_settings, update_settings

BACKGROUNDS = ('pulse', 'horizon', 'ember')
ASSETS = Path(__file__).parent / 'assets'


def selected_background():
    value = read_settings().get('background', 'pulse')
    return value if value in BACKGROUNDS else 'pulse'


def choose_background(name):
    if name not in BACKGROUNDS:
        raise ValueError('Fondo no disponible')
    update_settings(background=name)


def background_markup():
    name = selected_background()
    art = (ASSETS / f'appearance-{name}.html').read_text(encoding='utf-8')
    return ('<div class="dashboard-background" aria-hidden="true">'
            '<div class="appearance-enter background-enter-loaded"><div class="appearance-ambient">'
            f'<div class="appearance-stage"><div class="appearance-frame" data-background="{name}">'
            + art + '</div></div></div></div></div>')


def render_appearance(rail):
    st.html("<script>" + (ASSETS / "appearance.js").read_text(encoding="utf-8") + "</script>", unsafe_allow_javascript=True)
    with rail.container(key='appearance_footer'):
        with st.popover('Apariencia', key='dashboard_appearance', width='stretch'):
            with st.container(key='appearance_options'):
                st.markdown('<p class="appearance-label">Fondo del panel</p>', unsafe_allow_html=True)
                with st.container(key='appearance_swatches'):
                    selected = selected_background()
                    for name in BACKGROUNDS:
                        st.button('Fondo ' + name.title(), key='appearance_' + name,
                                  type='primary' if name == selected else 'secondary',
                                  on_click=choose_background, args=(name,))
