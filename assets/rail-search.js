(() => {
  window.__anonRailSearch?.destroy();
  let field;
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es').trim();
  function filter() {
    const query = normalize(field?.value || '');
    const rows = [...document.querySelectorAll('.st-key-document_history [data-testid="stVerticalBlock"][class*="st-key-history_row_"]')];
    let count = 0;
    for (const row of rows) {
      const button = row.querySelector('[data-testid="stButton"] button');
      if (!button) continue;
      const visible = normalize(button.querySelector('p')?.textContent || button.textContent).includes(query);
      row.dataset.searchHidden = String(!visible);
      if (row.parentElement?.getAttribute('data-testid') === 'stLayoutWrapper') {
        row.parentElement.dataset.searchHidden = String(!visible);
      }
      if (visible) count++;
    }
    const empty = document.querySelector('.rail-search-empty');
    if (empty) empty.hidden = !query || count > 0;
  }
  function bind() {
    if (document.querySelector('.st-key-history_rename_panel')) {
      document.querySelectorAll('[class*="st-key-history_more_"] button[aria-expanded="true"]').forEach(button => button.click());
    }
    const next = document.querySelector('.st-key-nav_search input');
    if (next !== field) {
      field?.removeEventListener('input', filter);
      field = next;
      field?.addEventListener('input', filter);
    }
    filter();
  }
  const observer = new MutationObserver(bind);
  observer.observe(document.body, {childList:true, subtree:true});
  bind();
  window.__anonRailSearch = {destroy() { observer.disconnect(); field?.removeEventListener('input', filter); }};
})();
