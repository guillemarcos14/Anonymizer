"""Local document conversation, following the user-selected Lovable editor.

Document strings are escaped before entering markup. Actions stay in the local app.
"""
import html
import json
from pathlib import Path
from urllib.parse import quote


_PATHS = {
    'copy': '<path d="M19 15h1a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-9a2 2 0 0 0-2 2v1"/><rect x="2" y="9" width="13" height="13" rx="2"/>',
    'edit': '<path d="m16 3 5 5M4 20l4-1L21 6a2.12 2.12 0 0 0-3-3L5 16l-1 4Z"/>',
    'link': '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    'up': '<path d="M7 10v10H4V10h3Zm0 0 5-7c2 0 3 2 2 4l-1 3h5a2 2 0 0 1 2 3l-2 6a2 2 0 0 1-2 1H7"/>',
    'down': '<g transform="rotate(180 12 12)"><path d="M7 10v10H4V10h3Zm0 0 5-7c2 0 3 2 2 4l-1 3h5a2 2 0 0 1 2 3l-2 6a2 2 0 0 1-2 1H7"/></g>',
    'more': '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
    'plus': '<path d="M12 6v12M6 12h12"/>',
    'chevron': '<path d="m7 10 5 5 5-5"/>',
    'voice': '<rect x="8" y="2.5" width="8" height="13" rx="4"/><path d="M5 11a7 7 0 0 0 14 0M12 18v4m-3 0h6"/>',
    'send': '<path d="M12 19V5m-5 5 5-5 5 5"/>',
    'close': '<path d="m6 6 12 12M6 18 18 6"/>',
    'review': '<path d="m5 12 4 4L19 6"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v.1"/>',
    'fullscreen': '<path d="M20 4 14 10m0-5v5h5M4 20l6-6m0 5v-5H5"/>',
}


def icon(name):
    reference = json.loads((Path(__file__).parent / 'assets' / 'workspace-icons.json').read_text(encoding='utf-8'))
    if name in reference:
        return reference[name]
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + _PATHS[name] + '</svg>'


def reference_icon_css():
    """Use the measured reference artwork in native Streamlit button targets."""
    rules = []
    for selector, name in [('.st-key-chat_send button', 'send'), ('.st-key-chat_fullscreen button', 'fullscreen')]:
        data = 'url("data:image/svg+xml,' + quote(icon(name), safe='') + '")'
        rules.append(selector + " [data-testid='stIconMaterial'] {display:none}")
        rules.append(selector + '::before {content:"";display:block;width:20px;height:20px;background:currentColor;mask:' + data + ' center/contain no-repeat}')
    mobile_chevron = 'url("data:image/svg+xml,' + quote(icon('chevron'), safe='') + '")'
    rules.append('@media(max-width:767px){.st-key-chat_fullscreen button::before{mask:' + mobile_chevron + ' center/contain no-repeat;transform:rotate(-90deg)}}')
    return '<style>' + '\n'.join(rules) + '</style>'


def action(name, label, action_name, extra=''):
    return '<button type="button" class="chat-action" data-chat-action="' + action_name + '" aria-label="' + html.escape(label, quote=True) + '" title="' + html.escape(label, quote=True) + '" ' + extra + '>' + icon(name) + '</button>'


def original_message(text):
    # Character references keep Markdown from creating paragraphs or links inside the bubble.
    source = html.escape(text).replace('\n', '&#10;').replace('\r', '&#13;')
    display = html.escape(text.rstrip('\r\n')).replace('\n', '&#10;').replace('\r', '&#13;')
    return ('<div class="chat-user-turn"><div class="chat-user-bubble" aria-label="Texto original">'
            '<div class="chat-user-text" id="anon-original-content">' + display + '</div>'
            '<button type="button" class="chat-message-toggle" data-chat-action="toggle-original" aria-expanded="false" aria-controls="anon-original-content" hidden>Mostrar más</button></div>'
            '<span class="chat-original-source" hidden>' + source + '</span>'
            '<div class="chat-user-toolbar">' + action('copy', 'Copiar original', 'copy-original') + action('edit', 'Editar original', 'edit') + '</div></div>')


def result_message(text):
    return '<div class="chat-assistant-text" aria-label="Texto anonimizado">' + html.escape(text) + '</div>'


def result_toolbar():
    return '<div class="chat-result-toolbar">' + action('up', 'Resultado útil', 'useful', 'aria-pressed="false"') + action('down', 'Necesita revisión', 'review', 'aria-pressed="false"') + action('copy', 'Copiar resultado anonimizado', 'copy-result') + action('more', 'Más opciones del resultado', 'more', 'aria-haspopup="menu" aria-expanded="false"') + '<span class="chat-copy-status" role="status" aria-live="polite"></span></div>'


def composer_controls():
    return '<div class="anon-composer-tools">' + action('plus', 'Acciones del documento', 'actions', 'aria-haspopup="menu" aria-expanded="false"') + '<button type="button" class="chat-mode" data-chat-action="settings" aria-label="Modo de anonimización">Anonimizar' + icon('chevron') + '</button><button type="button" class="chat-voice" disabled aria-label="Entrada de voz no disponible" title="Entrada de voz no disponible">' + icon('voice') + '</button></div>'


