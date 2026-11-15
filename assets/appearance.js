(() => {
 window.__anonAppearanceSize?.disconnect();
 const main = document.querySelector('[data-testid="stMain"]');
 if (!main) return;
 const sync = () => document.documentElement.style.setProperty('--appearance-vw', (main.clientWidth / 100) + 'px');
 const observer = new ResizeObserver(sync);
 observer.observe(main); sync();
 window.__anonAppearanceSize = observer;
})();
