/* HM Portfolio — folder-driven gallery renderer.
   Loaded after main.js so it can safely replace legacy gallery event bindings. */
(() => {
  const data = window.HM_GALLERY_DATA;
  if (!data) return;

  const esc = (s='') => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const naturalLabel = (entry, fallback) => entry?.title || fallback;

  function cloneReplace(el) {
    if (!el) return null;
    const clone = el.cloneNode(true);
    el.replaceWith(clone);
    return clone;
  }

  function readSaved(key) {
    try { return localStorage.getItem(key); } catch (_) { return null; }
  }

  function writeSaved(key, value) {
    try { localStorage.setItem(key, value); } catch (_) {}
  }

  // ---------- Selected Work ----------
  (() => {
    const grid = document.querySelector('.selected-work-grid');
    const oldLb = document.getElementById('selectedWorkLightbox');
    const items = data.selectedWork || [];
    if (!grid || !oldLb || !items.length) return;

    grid.innerHTML = items.map((entry, i) => `
      <button class="selected-work-item" type="button" data-hm-selected="${i}">
        <img src="${esc(entry.thumb)}" alt="${esc(naturalLabel(entry, `Selected work ${i+1}`))}" loading="lazy" decoding="async">
      </button>`).join('');

    const lb = cloneReplace(oldLb);
    const img = lb.querySelector('img');
    let index = 0;
    const show = i => {
      index = (i + items.length) % items.length;
      const entry = items[index];
      img.src = entry.preview || entry.original;
      img.alt = naturalLabel(entry, `Selected work ${index+1}`);
    };
    const open = i => { show(i); lb.classList.add('is-open'); lb.setAttribute('aria-hidden','false'); document.body.style.overflow='hidden'; };
    const close = () => { lb.classList.remove('is-open'); lb.setAttribute('aria-hidden','true'); document.body.style.overflow=''; };

    grid.querySelectorAll('[data-hm-selected]').forEach((b,i) => b.addEventListener('click', () => open(i)));
    lb.querySelector('#selectedWorkPrev')?.addEventListener('click', e => { e.stopPropagation(); show(index-1); });
    lb.querySelector('#selectedWorkNext')?.addEventListener('click', e => { e.stopPropagation(); show(index+1); });
    lb.querySelector('#selectedWorkClose')?.addEventListener('click', close);
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    window.addEventListener('keydown', e => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(index-1);
      if (e.key === 'ArrowRight') show(index+1);
    });
  })();

  // ---------- Practice ----------
  (() => {
    const grid = document.getElementById('bridgeGrid');
    const title = document.getElementById('bridgeCategoryTitle');
    const count = document.getElementById('bridgeCount');
    if (!grid || !title || !count) return;

    const categories = data.practice || {};
    const labels = {
      engineering:'Engineering', painting:'Painting & Digital Painting', photography:'Photography',
      'graphic-design':'Graphic Design', animation:'Animation', training:'Training'
    };
    const legacyToCanonical = {architecture:'engineering', painting:'painting', photography:'photography', graphic:'graphic-design', animation:'animation', education:'training'};
    const stateKey = 'hm-practice-category';

    const rawButtons = [...document.querySelectorAll('[data-gallery-category]')];
    const buttons = rawButtons.map(old => {
      const canonical = legacyToCanonical[old.dataset.galleryCategory] || old.dataset.galleryCategory;
      const clone = old.cloneNode(true);
      clone.dataset.galleryCategory = canonical;
      old.replaceWith(clone);
      return clone;
    });
    const shuffle = cloneReplace(document.getElementById('bridgeShuffle'));
    const lb = cloneReplace(document.getElementById('practiceLightbox'));
    if (!lb) return;
    const lbImg = lb.querySelector('#practiceLightboxImage');
    const lbCap = lb.querySelector('#practiceLightboxCaption');
    const remembered = readSaved(stateKey);
    let current = Object.prototype.hasOwnProperty.call(categories, remembered) ? remembered : 'engineering';
    let currentItems = [], currentIndex = 0;

    const shuffled = a => {
      a=[...a]; for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a;
    };
    function render(cat, random=false) {
      if (!Object.prototype.hasOwnProperty.call(categories, cat)) cat = 'engineering';
      current = cat;
      writeSaved(stateKey, current);
      buttons.forEach(b => b.classList.toggle('is-active', b.dataset.galleryCategory === cat));
      title.textContent = labels[cat] || cat;
      currentItems = random ? shuffled(categories[cat] || []) : [...(categories[cat] || [])];
      grid.innerHTML = currentItems.map((entry,i) => `
        <button class="bridge-item" type="button" data-hm-practice="${i}">
          <img src="${esc(entry.thumb)}" alt="${esc(naturalLabel(entry, `${labels[cat]} work ${i+1}`))}" loading="lazy" decoding="async">
          <span class="item-index">${String(i+1).padStart(2,'0')}</span>
        </button>`).join('');
      count.textContent = `${currentItems.length} items`;
      grid.querySelectorAll('[data-hm-practice]').forEach((b,i) => b.addEventListener('click', () => open(i)));
    }
    function show(i) {
      if (!currentItems.length) return;
      currentIndex = (i + currentItems.length) % currentItems.length;
      const entry = currentItems[currentIndex];
      lbImg.src = entry.preview || entry.original;
      lbImg.alt = naturalLabel(entry, `${labels[current]} work`);
      if (lbCap) lbCap.textContent = `${labels[current]} · ${String(currentIndex+1).padStart(2,'0')} / ${String(currentItems.length).padStart(2,'0')}`;
    }
    function open(i) { show(i); lb.classList.add('is-open'); lb.setAttribute('aria-hidden','false'); document.body.style.overflow='hidden'; }
    function close() { lb.classList.remove('is-open'); lb.setAttribute('aria-hidden','true'); document.body.style.overflow=''; }

    buttons.forEach(b => b.addEventListener('click', () => render(b.dataset.galleryCategory)));
    shuffle?.addEventListener('click', () => render(current, true));
    lb.querySelector('#practiceLightboxClose')?.addEventListener('click', close);
    lb.querySelector('#practiceLightboxPrev')?.addEventListener('click', () => show(currentIndex-1));
    lb.querySelector('#practiceLightboxNext')?.addEventListener('click', () => show(currentIndex+1));
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    window.addEventListener('keydown', e => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(currentIndex-1);
      if (e.key === 'ArrowRight') show(currentIndex+1);
    });
    render(current);
  })();

  // ---------- Knowledge ----------
  (() => {
    const grid = document.getElementById('knowledgeGallery');
    const title = document.getElementById('knowledgeCategoryTitle');
    const count = document.getElementById('knowledgeCount');
    const empty = document.getElementById('knowledgeEmpty');
    const shuffle = document.getElementById('knowledgeShuffle');
    if (!grid || !title) return;

    const categories = data.knowledge || {};
    const labels = {
      engineering:'Engineering', painting:'Painting & Digital Painting', photography:'Photography',
      'graphic-design':'Graphic Design', animation:'Animation', training:'Training'
    };
    const stateKey = 'hm-knowledge-category';
    const rawButtons = [...document.querySelectorAll('[data-knowledge-filter]')];
    const buttons = rawButtons.map(old => {
      const map = {graphic:'graphic-design'};
      const clone = old.cloneNode(true);
      clone.dataset.knowledgeFilter = map[old.dataset.knowledgeFilter] || old.dataset.knowledgeFilter;
      old.replaceWith(clone);
      return clone;
    });
    const lb = cloneReplace(document.getElementById('knowledgeLightbox'));
    if (!lb) return;
    const lbImg = lb.querySelector('#knowledgeLightboxImage');
    const lbCap = lb.querySelector('#knowledgeLightboxCaption');
    const remembered = readSaved(stateKey);
    let current = Object.prototype.hasOwnProperty.call(categories, remembered) ? remembered : 'engineering';
    let currentItems=[], currentIndex=0;

    function render(cat) {
      if (!Object.prototype.hasOwnProperty.call(categories, cat)) cat = 'engineering';
      current = cat;
      writeSaved(stateKey, current);
      currentItems = [...(categories[cat] || [])];
      buttons.forEach(b => b.classList.toggle('is-active', b.dataset.knowledgeFilter === cat));
      title.textContent = labels[cat] || cat;
      if (count) count.textContent = `${currentItems.length} items`;
      if (empty) empty.hidden = currentItems.length !== 0;
      grid.innerHTML = currentItems.map((entry,i) => `
        <button class="knowledge-thumb" type="button" data-hm-knowledge="${i}">
          <img src="${esc(entry.thumb)}" alt="${esc(naturalLabel(entry, `${labels[cat]} knowledge ${i+1}`))}" loading="lazy" decoding="async">
          <span class="knowledge-thumb-index">${String(i+1).padStart(2,'0')}</span>
        </button>`).join('');
      grid.querySelectorAll('[data-hm-knowledge]').forEach((b,i) => b.addEventListener('click', () => open(i)));
    }
    function show(i) {
      if (!currentItems.length) return;
      currentIndex = (i + currentItems.length) % currentItems.length;
      const entry = currentItems[currentIndex];
      lbImg.src = entry.preview || entry.original;
      lbImg.alt = naturalLabel(entry, `${labels[current]} knowledge`);
      if (lbCap) lbCap.textContent = `${labels[current]} · ${String(currentIndex+1).padStart(2,'0')} / ${String(currentItems.length).padStart(2,'0')}`;
    }
    function open(i) { show(i); lb.classList.add('is-open'); lb.setAttribute('aria-hidden','false'); document.body.style.overflow='hidden'; }
    function close() { lb.classList.remove('is-open'); lb.setAttribute('aria-hidden','true'); document.body.style.overflow=''; }

    buttons.forEach(b => b.addEventListener('click', () => render(b.dataset.knowledgeFilter)));
    lb.querySelector('#knowledgePrev')?.addEventListener('click', e => { e.stopPropagation(); show(currentIndex-1); });
    lb.querySelector('#knowledgeNext')?.addEventListener('click', e => { e.stopPropagation(); show(currentIndex+1); });
    lb.querySelector('#knowledgeClose')?.addEventListener('click', close);
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    window.addEventListener('keydown', e => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(currentIndex-1);
      if (e.key === 'ArrowRight') show(currentIndex+1);
    });
    render(current);
  })();
})();

/* HM Portfolio — restored full About biography */
(() => {
  const biography = document.querySelector('.about-biography');
  if (!biography) return;

  biography.innerHTML = `
    <p>Hassan Marji is a multidisciplinary creative professional whose career spans architecture, painting, photography, graphic design, education, and digital media. Born in Lebanon on December 6, 1967, his professional journey has developed at the intersection of artistic expression, design, technology, and communication.</p>

    <p>Over several decades, he has built extensive experience in architecture and visual communication while developing deep expertise in desktop publishing, video production, visual effects, 3D modeling, animation, photography, and digital design. His work includes projects undertaken in Lebanon and internationally, combining creative thinking with technical knowledge across disciplines that are often treated separately.</p>

    <p>Education and professional training have also formed an important part of his career. As a certified instructor for technologies and platforms including Adobe, Autodesk, and Apple, he has delivered specialized training programs for government institutions, television channels, production companies, universities, and other professional organizations.</p>

    <p>What distinguishes Marji's career is not simply the number of fields in which he has worked, but the connections between them. Architecture informs his understanding of space and structure; painting and photography shape his visual language; graphic design strengthens communication; and digital media provides the tools through which these disciplines increasingly converge.</p>

    <p>After decades of professional practice and teaching, he continues to explore new technologies and new ways of working, while maintaining the same underlying interest that has connected his career from the beginning: using creativity, knowledge, and technology to turn ideas into meaningful visual experiences.</p>
  `;
})();
