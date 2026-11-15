(() => {
  window.__anonComposerControls?.destroy();
  const cleanups = [];
  const popups = [];
  const bound = new WeakSet();
  let openTimer, closeTimer;
  function attach(button, name, align) {
    if (!button || bound.has(button)) return;
    bound.add(button);
    const popup = document.createElement('div');
    popup.id = `anon-features-${name}`;
    popup.className = 'anon-feature-popup';
    popup.setAttribute('popover', 'auto');
    popup.setAttribute('role', 'dialog');
    popup.setAttribute('aria-labelledby', `${popup.id}-title`);
    const heading = document.createElement('p');
    heading.className = 'anon-feature-title';
    heading.id = popup.id + '-title';
    heading.textContent = name === 'plus' ? 'Adjunta tus archivos' : 'Más posibilidades para tus archivos';
    const description = document.createElement('p');
    description.className = 'anon-feature-body';
    description.textContent = name === 'plus'
      ? 'Pronto podrás adjuntar archivos y anonimizar su contenido directamente desde aquí.'
      : 'Pronto tendrás nuevas herramientas para trabajar con tus archivos y proteger sus datos.';
    popup.append(heading, description);
    document.body.append(popup);
    popups.push(popup);
    button.setAttribute('aria-controls', popup.id);
    function position() {
      const r = button.getBoundingClientRect();
      const width = Math.min(288, innerWidth - 32);
      popup.style.left = `${Math.max(16, Math.min(align === 'start' ? r.left : r.right-width, innerWidth-width-16))}px`;
      const height = popup.getBoundingClientRect().height || 118;
      const bottom = r.bottom + 4;
      popup.style.top = `${bottom+height <= innerHeight-16 ? bottom : Math.max(16, r.top-height-4)}px`;
      popup.style.transformOrigin = align === 'start' ? '16px 0' : `${width-32}px 0`;
    }
    function show() {
      clearTimeout(openTimer); clearTimeout(closeTimer);
      popups.forEach(p => { if (p !== popup && p.matches(':popover-open')) p.hidePopover(); });
      if (!popup.matches(':popover-open')) popup.showPopover();
      position(); button.setAttribute('aria-expanded','true');
    }
    function hide() { if (popup.matches(':popover-open')) popup.hidePopover(); }
    function leave() { clearTimeout(openTimer); closeTimer=setTimeout(()=>{if(!popup.matches(':hover')&&!button.matches(':hover')&&!popup.contains(document.activeElement))hide();},200); }
    const listen=(e,event,fn)=>{e.addEventListener(event,fn);cleanups.push(()=>e.removeEventListener(event,fn));};
    listen(button,'pointerenter',()=>{clearTimeout(closeTimer);openTimer=setTimeout(show,300);});
    listen(button,'pointerleave',leave);
    listen(button,'click',show);
    listen(button,'focus',show);
    listen(button,'blur',leave);
    listen(popup,'pointerenter',()=>clearTimeout(closeTimer));
    listen(popup,'pointerleave',leave);
    listen(popup,'toggle',()=>button.setAttribute('aria-expanded',String(popup.matches(':popover-open'))));
    listen(window,'resize',()=>{if(popup.matches(':popover-open'))position();});
    listen(window,'scroll',()=>{if(popup.matches(':popover-open'))position();});
  }
  function syncSend() {
    const field = document.querySelector('.st-key-input_preview textarea');
    const send = document.querySelector('.st-key-anonymize_document button');
    if (field && send) {
      const empty = !field.value.trim();
      if (send.disabled !== empty) send.disabled = empty;
    }
  }
  document.addEventListener('input', syncSend);
  cleanups.push(() => document.removeEventListener('input', syncSend));
  function bind() {
    syncSend();
    attach(document.querySelector('.anon-add'),'plus','start');
    attach(document.querySelector('.anon-input-mode'),'mode','end');
  }
  const observer = new MutationObserver(bind);
  observer.observe(document.body,{childList:true,subtree:true});
  bind();
  window.__anonComposerControls = {destroy(){observer.disconnect();clearTimeout(openTimer);clearTimeout(closeTimer);cleanups.forEach(fn=>fn());popups.forEach(p=>p.remove());}};
})();
