"""Presentation for the user-pinned Lovable first-screen reference.

Artwork and type are bundled locally. Document text only enters Streamlit widgets.
"""
import base64
import os
import streamlit as st

_HERE = os.path.dirname(__file__)


def _brand_css() -> str:
    with open(os.path.join(_HERE, "assets", "fonts", "CameraPlainVariable.woff2"), "rb") as source:
        font_data = base64.b64encode(source.read()).decode("ascii")
    with open(os.path.join(_HERE, "anonimizar.css"), encoding="utf-8-sig") as source:
        css = source.read()
    for provider in ('google', 'github', 'apple'):
        with open(os.path.join(_HERE, 'assets', f'auth-{provider}.svg'), 'rb') as source:
            css = css.replace('__AUTH_' + provider.upper() + '_DATA__', base64.b64encode(source.read()).decode('ascii'))
    return "<style>" + css.replace("__CAMERA_DATA__", font_data) + "</style>"


def apply_branding() -> None:
    st.markdown(_brand_css(), unsafe_allow_html=True)


def motion_markup(state: str) -> str:
    """Expose real processing state, without interpolating document content."""
    labels = {
        'idle': '', 'loading': 'Anonimizando el texto…',
        'complete': 'Resultado disponible.', 'ready': 'Resultado disponible.',
        'error': 'No se pudo procesar el texto.',
    }
    if state not in labels:
        raise ValueError('Unknown presentation state')
    return f'<span class="anon-stage anon-stage--{state}" role="status" aria-live="polite">{labels[state]}</span>'


def hero_background() -> str:
    """Bundled vector artwork; no document content or remote requests."""
    with open(os.path.join(_HERE, "assets", "lovable-pulse.html"), encoding="utf-8") as source:
        return source.read()


def animate_placeholder() -> None:
    """Animate only the native placeholder; never write document text or values."""
    with open(os.path.join(_HERE, "assets", "placeholder.js"), encoding="utf-8") as source:
        placeholder = source.read()
    with open(os.path.join(_HERE, "assets", "entry-ready.js"), encoding="utf-8") as source:
        ready = source.read()
    with open(os.path.join(_HERE, "assets", "users-carousel.js"), encoding="utf-8") as source:
        users = source.read()
    st.html("<script>" + placeholder + "\n" + ready + "\n" + users + "</script>", unsafe_allow_javascript=True)
