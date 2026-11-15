(() => {
  window.__anonWorkspaceControls?.destroy();
  let menu, anchor;
  const cleanups = [];
  const trigger = key => document.querySelector(`.st-key-chat_tool_${key} button`)?.click();
  const close = () => { if (menu?.matches(':popover-open')) menu.hidePopover(); anchor?.setAttribute('aria-expanded', 'false'); };
  function popup(button) {
    close();
    menu?.remove();
    anchor = button;
    menu = document.createElement('div');
    menu.className = 'chat-context-menu';
    menu.setAttribute('popover', 'auto');
    menu.setAttribute('role', 'menu');
    [['Editar original', 'original'], ['Revisar personas', 'review'], ['Datos detectados', 'findings'], ['Configuración', 'settings'], ['Descargar resultado', 'download']].forEach(([label, key]) => {
      const item = document.createElement('button');
      item.type = 'button'; item.textContent = label; item.setAttribute('role', 'menuitem');
      item.addEventListener('click', () => { close(); key === 'download' ? download() : trigger(key); });
      menu.append(item);
    });
    document.body.append(menu); menu.showPopover();
    const r = button.getBoundingClientRect(), m = menu.getBoundingClientRect();
    menu.style.left = `${Math.max(8, Math.min(r.left, innerWidth - m.width - 8))}px`;
    menu.style.top = `${r.top > m.height + 8 ? r.top - m.height - 4 : r.bottom + 4}px`;
    button.setAttribute('aria-expanded', 'true');
    menu.addEventListener('toggle', () => button.setAttribute('aria-expanded', String(menu.matches(':popover-open'))));
    menu.querySelector('button')?.focus();
  }
  const result = () => document.querySelector('.chat-assistant-text')?.textContent ?? document.querySelector('.chat-highlight-source')?.textContent;
  function download() {
    const text = result(); if (text == null) return;
    const url = URL.createObjectURL(new Blob([text], {type:'text/plain;charset=utf-8'}));
    const link = document.createElement('a'); link.href = url; link.download = 'anonimizado.txt'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  async function clicked(event) {
    const button = event.target.closest('[data-chat-action]');
    if (!button) return;
    const action = button.dataset.chatAction;
    if (action === 'toggle-original') {
      const expanded = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(expanded));
      button.textContent = expanded ? 'Mostrar menos' : 'Mostrar más';
      button.closest('.chat-user-bubble').querySelector('.chat-user-text')?.classList.toggle('is-expanded', expanded);
      return;
    }
    if (action === 'edit') return trigger('original');
    if (['settings','review'].includes(action)) return trigger(action);
    if (['actions','more'].includes(action)) return popup(button);
    if (action === 'useful') {
      const active = button.getAttribute('aria-pressed') !== 'true';
      button.setAttribute('aria-pressed', String(active));
      button.closest('.chat-result-toolbar').querySelector('.chat-copy-status').textContent = active ? 'Marcado como útil en esta vista' : '';
      return;
    }
    if (action.startsWith('copy-')) {
      const text = action === 'copy-original' ? document.querySelector('.chat-original-source')?.textContent : result();
      if (text == null) return;
      const status = document.querySelector('.chat-copy-status');
      try {
        // The native copy event also reaches embedded browsers whose async
        // Clipboard implementation resolves without updating the host clipboard.
        const field = document.createElement('textarea');
        field.value = text; field.setAttribute('aria-hidden','true');
        field.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0';
        document.body.append(field); field.select();
        let copied = false;
        try { copied = document.execCommand('copy'); } finally { field.remove(); button.focus(); }
        if (!copied) await navigator.clipboard.writeText(text);
        if(status) status.textContent = 'Copiado';
      }
      catch { if(status) status.textContent = 'Selecciona el texto y cópialo con el teclado.'; }
    }
  }
  function mobileDetails(event) {
    if (matchMedia('(max-width:767px)').matches && event.target.closest('.st-key-chat_fullscreen button')) {
      event.preventDefault(); event.stopPropagation(); trigger('findings');
    }
  }
  function keydown(event) {
    if (event.key === 'Escape') {
      close();
      if (document.querySelector('.workspace-tool-review,.workspace-tool-settings,.workspace-tool-findings')) document.querySelector('.st-key-chat_close_details button')?.click();
    }

  }
  let originalNode;
  function syncOriginal() {
    const text = document.querySelector('.chat-user-text');
    const toggle = document.querySelector('.chat-message-toggle');
    if (!text || !toggle) return;
    const overflow = text.scrollHeight > parseFloat(getComputedStyle(text).lineHeight) * 4 + 1;
    toggle.hidden = !overflow;
    if (!overflow && toggle.getAttribute('aria-expanded') === 'true') {
      toggle.setAttribute('aria-expanded', 'false');
      toggle.textContent = 'Mostrar más';
      text.classList.remove('is-expanded');
    }
  }
  const originalResize = new ResizeObserver(syncOriginal);
  document.fonts.ready.then(syncOriginal);
  function hydrate() {
    const nextOriginal = document.querySelector('.chat-user-text');
    if (nextOriginal !== originalNode) {
      originalResize.disconnect();
      originalNode = nextOriginal;
      if (originalNode) originalResize.observe(originalNode);
    }
    syncOriginal();
    const draft = document.querySelector('.st-key-original_editor textarea');
    const submit = document.querySelector('.st-key-original_editor .st-key-anonymize_document button');
    if (draft && submit) submit.disabled = !draft.value.trim();
    const field = document.querySelector('.st-key-chat_composer textarea');
    const send = document.querySelector('.st-key-chat_send button');
    if (field && send) {
      send.disabled = !field.value.trim();
      send.setAttribute('aria-label', 'Enviar texto');
    }
    const expand = document.querySelector('.st-key-chat_fullscreen button');
    if (expand && matchMedia('(max-width:767px)').matches) expand.setAttribute('aria-label', 'Abrir detalles del documento');
  }
  document.addEventListener('click', clicked);
  document.addEventListener('click', mobileDetails, true);
  document.addEventListener('keydown', keydown);
  document.addEventListener('input', hydrate);
  const observer = new MutationObserver(hydrate);
  observer.observe(document.body, {childList:true, subtree:true}); hydrate();
  window.__anonWorkspaceControls = {destroy() { close(); menu?.remove(); observer.disconnect(); originalResize.disconnect(); document.removeEventListener('click', clicked); document.removeEventListener('click', mobileDetails, true); document.removeEventListener('keydown', keydown); document.removeEventListener('input', hydrate); cleanups.forEach(fn=>fn()); }};
})();
