(() => {
  window.__anonComposerEnter?.destroy();
  function keydown(event) {
    const field = event.target;
    if (!(field instanceof HTMLTextAreaElement) ||
        !field.matches('.st-key-input_preview textarea, .st-key-chat_composer textarea') ||
        event.key !== 'Enter' || event.shiftKey || event.altKey ||
        event.isComposing || event.keyCode === 229) return;
    event.preventDefault();
    event.stopPropagation();
    if (event.repeat || !field.value.trim()) return;
    const selector = field.closest('.st-key-chat_composer')
      ? '.st-key-chat_send button' : '.st-key-anonymize_document button';
    // Blur commits Streamlit's textarea value before its existing send callback.
    field.blur();
    setTimeout(() => {
      const send = document.querySelector(selector);
      if (send && !send.disabled) send.click();
    }, 0);
  }
  document.addEventListener('keydown', keydown, true);
  window.__anonComposerEnter = {destroy() { document.removeEventListener('keydown', keydown, true); }};
})();
