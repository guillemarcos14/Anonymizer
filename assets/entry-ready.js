(() => {
  window.__anonEntryReady?.disconnect();
  let waitingForFont = false;
  function reveal() {
    const hero = document.querySelector('.st-key-entry_hero');
    const panel = hero?.querySelector('.st-key-input_panel');
    if (!panel || !panel.querySelector('textarea') ||
        !panel.querySelector('.st-key-input_footer .stButton button') ||
        !panel.querySelector('.anon-composer-tools')) return;
    if (waitingForFont) return;
    waitingForFont = true;
    // Visibility keeps layout and font loading active while controls are mounting.
    document.fonts.load('16px "Camera Plain Variable"').catch(() => []).then(() => {
      if (!panel.isConnected) { waitingForFont = false; reveal(); return; }
      panel.classList.add('anon-composer-ready');
      observer.disconnect();
    });
  }
  const observer = new MutationObserver(reveal);
  window.__anonEntryReady = observer;
  observer.observe(document.body, { childList: true, subtree: true });
  reveal();
})();
