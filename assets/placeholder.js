(() => {
  // Timing follows Lovable's public typewriter hook; all copy and execution are local.
  const existing = document.querySelector('.st-key-input_preview textarea');
  if (existing && window.__anonPlaceholder?.field === existing) return;
  window.__anonPlaceholder?.destroy();
  const prefix = 'Pega ';
  const words = [
    'el texto que quieres anonimizar…',
    'un correo para revisar sus datos personales…',
    'una conversación para anonimizar sus datos…',
  ];
  const selector = '.st-key-input_preview textarea';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const fallback = prefix + words[0];
  let timer, field, index = 0, text = fallback, deleting = false, stopped = false;
  const later = ms => { timer = window.setTimeout(tick, ms); };
  function tick() {
    if (stopped) return;
    const next = document.querySelector(selector);
    if (next !== field) { field = next; index = 0; text = fallback; deleting = false; }
    if (!field) { later(100); return; }
    if (reduced.matches || document.hidden || field.value.length > 0) {
      field.placeholder = fallback;
      later(200);
      return;
    }
    const target = prefix + words[index];
    if (!deleting) {
      if (text === target) { deleting = true; later(30); return; }
      text = target.slice(0, text.length + 1);
      field.placeholder = text;
      later(text === target ? 1500 : 30);
      return;
    }
    if (text.length > prefix.length) {
      text = text.slice(0, -1);
      field.placeholder = text;
      if (text.length > prefix.length) { later(30); return; }
    }
    index = (index + 1) % words.length;
    deleting = false;
    later(30);
  }
  window.__anonPlaceholder = {
    get field() { return field; },
    destroy() { stopped = true; window.clearTimeout(timer); },
  };
  // Start from the server-rendered phrase, hold it, then erase and type normally.
  // Reruns keep the current phrase rather than resetting a visible field.
  field = document.querySelector(selector);
  if (field) text = field.placeholder;
  later(1500);
})();
