for (const r of document.querySelectorAll('.region')) {
  const reads = r.querySelector('.reads'), ring = r.querySelector('.ring');
  const place = (e) => { const b = r.getBoundingClientRect(); const x = e.clientX - b.left, y = e.clientY - b.top;
    reads.style.clipPath = 'circle(80px at ' + x + 'px ' + y + 'px)'; ring.style.left = x + 'px'; ring.style.top = y + 'px'; r.dataset.lens = 'on'; };
  r.addEventListener('pointermove', (e) => { if (e.pointerType === 'touch' && r.dataset.lens !== 'on') return; place(e); });
  r.addEventListener('pointerleave', () => { r.dataset.lens = 'off'; });
  let t = null;
  r.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'touch') return; t = setTimeout(() => place(e), 350); });
  const up = () => { if (t) clearTimeout(t); t = null; r.dataset.lens = 'off'; };
  r.addEventListener('pointerup', up); r.addEventListener('pointercancel', up);
}
