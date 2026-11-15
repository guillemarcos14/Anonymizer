(() => {
  // Repeated Streamlit renders must never duplicate listeners or animation loops.
  window.__anonUsersCarousel?.dispose();
  const initials = ['C', 'D', 'A', 'M', 'L', 'J', 'S', 'P'];
  const colors = ['#272725', '#a83800', '#315fc4', '#70459b', '#196b50', '#a1405c', '#725b14', '#356479'];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let pill, track, index = 0, timer, active = false, hovered = false;
  function render() {
    track.classList.remove('is-moving');
    track.replaceChildren(...Array.from({length: 4}, (_, slot) => {
      const circle = document.createElement('span');
      const person = (index + slot) % initials.length;
      circle.textContent = initials[person];
      circle.style.color = colors[person];
      circle.style.zIndex = slot;
      return circle;
    }));
  }
  function step() {
    if (!active || !pill.isConnected) return;
    // Commit the reset before the next 18px transition (200ms + 50ms pause).
    track.getBoundingClientRect();
    track.classList.add('is-moving');
    timer = setTimeout(() => {
      index = (index + 1) % initials.length;
      render();
      if (active) timer = setTimeout(step, 50);
    }, 200);
  }
  function stop() {
    active = false;
    clearTimeout(timer);
    if (track) {
      if (track.classList.contains('is-moving')) index = (index + 1) % initials.length;
      render();
    }
  }
  function start() {
    if (active || reduced.matches || document.hidden || !hovered) return;
    active = true;
    step();
  }
  function enter() { hovered = true; start(); }
  function leave() { hovered = false; stop(); }
  function visibility() { if (document.hidden) stop(); else start(); }
  function preference() { stop(); start(); }
  function bind() {
    const next = document.querySelector('.dashboard-pill');
    if (next === pill) return;
    stop();
    pill?.removeEventListener('pointerenter', enter);
    pill?.removeEventListener('pointerleave', leave);
    pill = next;
    track = pill?.querySelector('.pill-track');
    hovered = false;
    if (!track) return;
    render();
    pill.addEventListener('pointerenter', enter);
    pill.addEventListener('pointerleave', leave);
  }
  const observer = new MutationObserver(bind);
  observer.observe(document.body, {childList:true, subtree:true});
  document.addEventListener('visibilitychange', visibility);
  reduced.addEventListener('change', preference);
  window.__anonUsersCarousel = {dispose() {
    observer.disconnect();
    stop();
    pill?.removeEventListener('pointerenter', enter);
    pill?.removeEventListener('pointerleave', leave);
    document.removeEventListener('visibilitychange', visibility);
    reduced.removeEventListener('change', preference);
  }};
  bind();
})();
