// HM image variants: thumbnails for grids, previews for large viewers.
function hmImageVariant(src, kind = 'previews') {
  if (!src || !src.startsWith('images/') || /\.(gif|svg|webp)$/i.test(src)) return src;
  const dot = src.lastIndexOf('.');
  if (dot < 0) return src;
  return `images/${kind}/${src.slice(7, dot)}.webp`;
}

document.querySelectorAll('.site-nav a').forEach(link => {
  link.addEventListener('click', () => {
    // Horizontal navigation stays permanently visible.
  });
});

/* v1.21 — Interactive practice image cube with discipline pools */
(() => {
  const canvas = document.getElementById('practice3d');
  const stage = document.getElementById('threeStage');
  const caption = document.getElementById('cubeCaption');
  const choices = Array.from(document.querySelectorAll('.discipline-choice'));
  if (!canvas || !stage) return;

  if (typeof THREE === 'undefined') {
    const msg = document.createElement('p');
    msg.className = 'three-fallback';
    msg.textContent = 'The 3D practice cube could not load.';
    stage.appendChild(msg);
    return;
  }

  const pools = {
    architecture: Array.from({length:14}, (_,i) => `images/practice/architecture/${String(i+1).padStart(2,'0')}.png`),
    painting: Array.from({length:16}, (_,i) => `images/practice/painting/${String(i+1).padStart(2,'0')}.png`),
    photography: [
      'images/practice/photography/01.jpeg',
      ...Array.from({length:14}, (_,i) => `images/practice/photography/${String(i+2).padStart(2,'0')}.jpg`),
      ...Array.from({length:10}, (_,i) => `images/practice/photography/${String(i+16).padStart(2,'0')}.jpeg`)
    ],
    animation: Array.from({length:12}, (_,i) => `images/practice/animation/${String(i+1).padStart(2,'0')}.svg`),
    education: Array.from({length:19}, (_,i) => {
      const names = [
        '01-capsat-exhibition.jpg','02-media-exhibition.jpg','03-adms-training.jpg','04-adms-certificate.jpg','05-adms-group.jpg',
        '06-training-2004.jpg','07-training-2005.jpg','08-adobe-workshop.jpg','09-after-effects-class.jpg','10-one-to-one-training.jpg',
        '11-event-demo.jpg','12-training-session.jpg','13-aramco-training.jpg','14-training-group-modern.jpg','15-class-selfie.jpg',
        '16-workshop-collaboration.jpg','17-training-group.jpg','18-lab-session.jpg','19-adobe-session.jpg'
      ];
      return `images/education/${names[i]}`;
    }),
    graphic: Array.from({length:12}, (_,i) => `graphic:${i+1}`)
  };

  const names = {
    architecture: 'Engineering',
    painting: 'Painting & Digital Painting',
    photography: 'Photography',
    graphic: 'Graphic Design',
    animation: 'Animation',
    education: 'Training'
  };

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 0, 9.4);

  const geometry = new THREE.BoxGeometry(3.15, 3.15, 3.15);
  const materials = Array.from({length:6}, () => new THREE.MeshBasicMaterial({color:0x151515}));
  const cube = new THREE.Mesh(geometry, materials);
  cube.rotation.x = THREE.MathUtils.degToRad(-14);
  cube.rotation.y = THREE.MathUtils.degToRad(31);
  scene.add(cube);

  const edgeGeo = new THREE.EdgesGeometry(geometry);
  const edgeMat = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.28 });
  cube.add(new THREE.LineSegments(edgeGeo, edgeMat));

  const faceStates = Array.from({length:6}, () => ({discipline:'architecture', src:null}));
  let selectedMode = 'architecture';
  const imageCache = new Map();

  function placeholderTexture(label='Loading') {
    const c=document.createElement('canvas'); c.width=c.height=900;
    const x=c.getContext('2d');
    x.fillStyle='#101010'; x.fillRect(0,0,900,900);
    x.strokeStyle='rgba(255,255,255,.22)'; x.lineWidth=3; x.strokeRect(3,3,894,894);
    x.fillStyle='#f2eee6'; x.font='300 46px Arial'; x.fillText(label,56,820);
    const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t;
  }

  function graphicTexture(n) {
    const c=document.createElement('canvas'); c.width=c.height=1000;
    const x=c.getContext('2d');
    x.fillStyle='#0a0a0a'; x.fillRect(0,0,1000,1000);
    x.strokeStyle='rgba(242,238,230,.34)'; x.lineWidth=3; x.strokeRect(34,34,932,932);
    x.fillStyle='#f7941d'; x.fillRect(74,78,14,844);
    x.strokeStyle='rgba(247,148,29,.32)'; x.lineWidth=2;
    for(let i=0;i<9;i++){ x.beginPath(); x.moveTo(160+i*82,120); x.lineTo(860-i*55,860); x.stroke(); }
    x.fillStyle='#aaa69f'; x.font='500 28px Arial'; x.fillText('GRAPHIC DESIGN / PLACEHOLDER',130,120);
    x.fillStyle='#f2eee6'; x.font='300 82px Arial'; x.fillText('Visual',130,430); x.fillText('Communication',130,525);
    x.fillStyle='#f7941d'; x.font='700 40px Arial'; x.fillText(String(n).padStart(2,'0'),130,640);
    x.fillStyle='#aaa69f'; x.font='300 26px Arial'; x.fillText('Temporary study — final work to be added.',130,855);
    const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t;
  }

  function coverTexture(src, onReady) {
    if (src.startsWith('graphic:')) { onReady(graphicTexture(+src.split(':')[1])); return; }
    if (imageCache.has(src)) { onReady(imageCache.get(src)); return; }
    const img = new Image();
    img.onload = () => {
      const c=document.createElement('canvas'); c.width=c.height=1000;
      const x=c.getContext('2d');
      const scale=Math.max(1000/img.width,1000/img.height);
      const w=img.width*scale,h=img.height*scale;
      x.drawImage(img,(1000-w)/2,(1000-h)/2,w,h);
      const grad=x.createLinearGradient(0,690,0,1000); grad.addColorStop(0,'rgba(0,0,0,0)'); grad.addColorStop(1,'rgba(0,0,0,.2)'); x.fillStyle=grad; x.fillRect(0,0,1000,1000);
      const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=renderer.capabilities.getMaxAnisotropy();
      imageCache.set(src,t); onReady(t);
    };
    img.onerror = () => onReady(placeholderTexture('Image unavailable'));
    img.src=src;
  }

  function shuffledUnique(pool, count=6) {
    const arr=[...pool];
    for(let i=arr.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [arr[i],arr[j]]=[arr[j],arr[i]]; }
    return arr.slice(0,Math.min(count,arr.length));
  }

  function setFace(faceIndex, discipline, src) {
    faceStates[faceIndex] = {discipline,src};
    materials[faceIndex].map = placeholderTexture(names[discipline] || 'Practice');
    materials[faceIndex].color.set(0xffffff); materials[faceIndex].needsUpdate=true;
    coverTexture(src, tex => {
      materials[faceIndex].map = tex; materials[faceIndex].needsUpdate=true;
    });
  }

  function fillDiscipline(discipline) {
    selectedMode=discipline;
    const picks=shuffledUnique(pools[discipline],6);
    for(let i=0;i<6;i++) setFace(i,discipline,picks[i % picks.length]);
    caption.textContent=names[discipline];
    choices.forEach(b=>b.classList.toggle('is-active',b.dataset.discipline===discipline));
  }

  function fillShuffle() {
    selectedMode='shuffle';
    const ds=Object.keys(names);
    const bag=[...ds]; while(bag.length<6) bag.push(...ds);
    for(let i=bag.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [bag[i],bag[j]]=[bag[j],bag[i]]; }
    for(let i=0;i<6;i++){
      const d=bag[i]; const pool=pools[d]; setFace(i,d,pool[Math.floor(Math.random()*pool.length)]);
    }
    caption.textContent='Shuffle / Random';
    choices.forEach(b=>b.classList.toggle('is-active',b.dataset.discipline==='shuffle'));
  }

  function changeOneFace(faceIndex) {
    const state=faceStates[faceIndex]; if(!state) return;
    const pool=pools[state.discipline]; if(!pool?.length) return;
    const visible = new Set(faceStates.filter((_,i)=>i!==faceIndex && faceStates[i].discipline===state.discipline).map(s=>s.src));
    let candidates=pool.filter(s=>s!==state.src && !visible.has(s));
    if(!candidates.length) candidates=pool.filter(s=>s!==state.src);
    if(!candidates.length) return;
    const src=candidates[Math.floor(Math.random()*candidates.length)];
    setFace(faceIndex,state.discipline,src);
    caption.textContent=names[state.discipline];
  }

  choices.forEach(btn=>btn.addEventListener('click',()=>{
    const d=btn.dataset.discipline;
    d==='shuffle' ? fillShuffle() : fillDiscipline(d);
  }));

  const raycaster=new THREE.Raycaster(); const pointer=new THREE.Vector2();
  let dragging=false,moved=false,lastX=0,lastY=0,downX=0,downY=0,velocityX=0,velocityY=0;
  function resize(){ const r=stage.getBoundingClientRect(); const w=Math.max(1,r.width),h=Math.max(1,r.height); renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix(); camera.position.z=w<700?10.5:9.4; }
  function hitFace(e){ const r=canvas.getBoundingClientRect(); pointer.x=((e.clientX-r.left)/r.width)*2-1; pointer.y=-((e.clientY-r.top)/r.height)*2+1; raycaster.setFromCamera(pointer,camera); const hits=raycaster.intersectObject(cube,false); return hits[0]?.face?.materialIndex ?? -1; }
  stage.addEventListener('pointerdown',e=>{ dragging=true;moved=false;lastX=downX=e.clientX;lastY=downY=e.clientY;velocityX=velocityY=0;stage.setPointerCapture(e.pointerId);stage.style.cursor='grabbing'; });
  stage.addEventListener('pointermove',e=>{ if(!dragging) return; const dx=e.clientX-lastX,dy=e.clientY-lastY; if(Math.hypot(e.clientX-downX,e.clientY-downY)>5)moved=true; cube.rotation.y+=dx*.007; cube.rotation.x+=dy*.0055; cube.rotation.x=Math.max(-1.35,Math.min(1.35,cube.rotation.x)); velocityY=dx*.007;velocityX=dy*.0055;lastX=e.clientX;lastY=e.clientY; });
  stage.addEventListener('pointerup',e=>{ dragging=false;try{stage.releasePointerCapture(e.pointerId)}catch(_){} stage.style.cursor='grab'; if(!moved){ const fi=hitFace(e); if(fi>=0) changeOneFace(fi); } });
  stage.addEventListener('pointercancel',()=>dragging=false);
  window.addEventListener('resize',resize); resize(); fillDiscipline('architecture');
  function render(){ if(!dragging){ cube.rotation.y+=velocityY; cube.rotation.x+=velocityX; velocityY*=.94;velocityX*=.94; } renderer.render(scene,camera); requestAnimationFrame(render); } render();
})();

// v1.6 — interactive mosaic reveal
(() => {
  const hero = document.querySelector('.hero');
  const grid = document.getElementById('mosaicReveal');
  if (!hero || !grid) return;

  let tiles = [], cols = 20, rows = 11, leaveTimer;

  function buildGrid() {
    const s = getComputedStyle(hero);
    cols = parseInt(s.getPropertyValue('--mosaic-cols')) || 20;
    rows = parseInt(s.getPropertyValue('--mosaic-rows')) || 11;
    grid.innerHTML = '';
    tiles = [];

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const t = document.createElement('span');
        t.className = 'mosaic-tile';
        t.dataset.col = c; t.dataset.row = r;
        t.style.backgroundSize = `${cols * 100}% ${rows * 100}%`;
        t.style.backgroundPosition =
          `${cols > 1 ? c/(cols-1)*100 : 0}% ${rows > 1 ? r/(rows-1)*100 : 0}%`;
        grid.appendChild(t);
        tiles.push(t);
      }
    }
  }

  function reveal(x, y) {
    clearTimeout(leaveTimer);
    const rect = grid.getBoundingClientRect();
    const cw = rect.width / cols, ch = rect.height / rows;
    const ac = (x - rect.left) / cw, ar = (y - rect.top) / ch;
    const radius = 2.35;

    tiles.forEach(t => {
      const dx = (+t.dataset.col + .5) - ac;
      const dy = (+t.dataset.row + .5) - ar;
      const d = Math.hypot(dx, dy);
      if (d <= radius) {
        t.style.transitionDelay = `${d * 28}ms`;
        t.classList.add('is-revealed');
      }
    });
  }

  hero.addEventListener('pointermove', e => reveal(e.clientX, e.clientY));
  hero.addEventListener('pointerdown', e => reveal(e.clientX, e.clientY));
  hero.addEventListener('pointerleave', () => {
    leaveTimer = setTimeout(() => {
      tiles.forEach(t => {
        t.style.transitionDelay = '0ms';
        t.classList.remove('is-revealed');
      });
    }, 220);
  });

  buildGrid();
  window.addEventListener('resize', () => setTimeout(buildGrid, 100));
})();




// v1.10 — Education gallery: reliable thumbnail selection + drag scrolling
(() => {
  const images = ['images/education/01-capsat-exhibition.jpg', 'images/education/02-media-exhibition.jpg', 'images/education/03-adms-training.jpg', 'images/education/04-adms-certificate.jpg', 'images/education/05-adms-group.jpg', 'images/education/06-training-2004.jpg', 'images/education/07-training-2005.jpg', 'images/education/08-adobe-workshop.jpg', 'images/education/09-after-effects-class.jpg', 'images/education/10-one-to-one-training.jpg', 'images/education/11-event-demo.jpg', 'images/education/12-training-session.jpg', 'images/education/13-aramco-training.jpg', 'images/education/14-training-group-modern.jpg', 'images/education/15-class-selfie.jpg', 'images/education/16-workshop-collaboration.jpg', 'images/education/17-training-group.jpg', 'images/education/18-lab-session.jpg', 'images/education/19-adobe-session.jpg'];
  const main = document.getElementById('eduMainImage');
  const mainButton = document.querySelector('.edu-main-open');
  const strip = document.getElementById('eduFilmstrip');
  const thumbs = Array.from(document.querySelectorAll('.edu-thumb'));
  const counter = document.getElementById('eduCounter');
  const download = document.getElementById('eduDownload');
  const prev = document.getElementById('eduPrev');
  const next = document.getElementById('eduNext');

  const lightbox = document.getElementById('eduLightbox');
  const lightboxImage = document.getElementById('eduLightboxImage');
  const lightboxCounter = document.getElementById('eduLightboxCounter');
  const lightboxDownload = document.getElementById('eduLightboxDownload');
  const lightboxClose = document.getElementById('eduLightboxClose');
  const lightboxPrev = document.getElementById('eduLightboxPrev');
  const lightboxNext = document.getElementById('eduLightboxNext');

  if (!main || !strip || !thumbs.length) return;

  let index = 0;
  const pad = n => String(n).padStart(2, '0');

  function update(nextIndex, scrollThumb = true) {
    index = (nextIndex + images.length) % images.length;

    

    const finish = () => {
      main.src = images[index];
      main.alt = `Education and training archive photograph ${index + 1}`;
      counter.textContent = `${pad(index + 1)} / ${pad(images.length)}`;
      download.href = images[index];

      thumbs.forEach((thumb, i) => {
        thumb.classList.toggle('is-active', i === index);
        thumb.setAttribute('aria-current', i === index ? 'true' : 'false');
      });

      if (scrollThumb) {
        thumbs[index].scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'nearest'
        });
      }

      if (lightbox?.classList.contains('is-open')) updateLightbox();
      requestAnimationFrame(() => mainButton?.classList.remove('is-changing'));
    };

    // Update immediately so clicking a thumbnail always changes the focus image.
    finish();
  }

  function updateLightbox() {
    lightboxImage.src = images[index];
    lightboxCounter.textContent = `${pad(index + 1)} / ${pad(images.length)}`;
    lightboxDownload.href = images[index];
  }

  // Explicit thumbnail selection. This is independent from the drag logic.
  thumbs.forEach((thumb, i) => {
    thumb.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      if (strip.dataset.wasDragged === 'true') return;
      update(i, false);
    });
  });

  prev?.addEventListener('click', () => update(index - 1));
  next?.addEventListener('click', () => update(index + 1));

  function openLightbox() {
    updateLightbox();
    lightbox.classList.add('is-open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lightbox.classList.remove('is-open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  mainButton?.addEventListener('click', openLightbox);
  lightboxClose?.addEventListener('click', closeLightbox);
  lightboxPrev?.addEventListener('click', () => update(index - 1));
  lightboxNext?.addEventListener('click', () => update(index + 1));

  lightbox?.addEventListener('click', e => {
    if (e.target === lightbox) closeLightbox();
  });

  document.addEventListener('keydown', e => {
    if (!lightbox?.classList.contains('is-open')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') update(index - 1);
    if (e.key === 'ArrowRight') update(index + 1);
  });

  // Drag-to-scroll without stealing normal thumbnail clicks.
  let dragging = false;
  let moved = false;
  let startX = 0, startY = 0, startLeft = 0, startTop = 0;
  const dragThreshold = 7;

  strip.addEventListener('pointerdown', e => {
    if (e.button !== undefined && e.button !== 0) return;
    dragging = true;
    moved = false;
    strip.dataset.wasDragged = 'false';
    startX = e.clientX;
    startY = e.clientY;
    startLeft = strip.scrollLeft;
    startTop = strip.scrollTop;
  });

  window.addEventListener('pointermove', e => {
    if (!dragging) return;

    const dx = e.clientX - startX;
    const dy = e.clientY - startY;

    if (!moved && Math.hypot(dx, dy) > dragThreshold) {
      moved = true;
      strip.classList.add('is-dragging');
      strip.dataset.wasDragged = 'true';
    }

    if (moved) {
      strip.scrollLeft = startLeft - dx;
      strip.scrollTop = startTop - dy;
      e.preventDefault();
    }
  }, { passive: false });

  window.addEventListener('pointerup', () => {
    if (!dragging) return;
    dragging = false;
    strip.classList.remove('is-dragging');

    // Keep the dragged state long enough to suppress the synthetic click,
    // then restore normal click behavior.
    setTimeout(() => {
      strip.dataset.wasDragged = 'false';
    }, 80);
  });

  window.addEventListener('pointercancel', () => {
    dragging = false;
    strip.classList.remove('is-dragging');
    strip.dataset.wasDragged = 'false';
  });
})();


/* v1.25 — Bridge-style practice browser and Knowledge page-flip */
(() => {
  const pools = {"architecture": ["images/practice/architecture/01.png", "images/practice/architecture/02.png", "images/practice/architecture/03.png", "images/practice/architecture/04.png", "images/practice/architecture/05.png", "images/practice/architecture/06.png", "images/practice/architecture/07.png", "images/practice/architecture/08.png", "images/practice/architecture/09.png", "images/practice/architecture/10.png", "images/practice/architecture/11.png", "images/practice/architecture/12.png", "images/practice/architecture/13.png", "images/practice/architecture/14.png", "images/practice/architecture/Nohad render 01.png", "images/practice/architecture/Visualization_01.jpg", "images/practice/architecture/Visualization_16.jpg", "images/practice/architecture/Visualization_21.jpg", "images/practice/architecture/a_detailed_pen_and_wash_architectural_sketch_ink_d.png", "images/practice/architecture/a_watercolor_and_ink_architectural_sketch_painting.png", "images/practice/architecture/architectural_corbel_sketch_with_distant_hills.png", "images/practice/architecture/architectural_sketch_of_a_mediterranean_stone_hous.png", "images/practice/architecture/mediterranean_villa_architectural_sketch.png", "images/practice/architecture/terracotta_roofed_stone_villa_sketch.png"], "painting": ["images/practice/painting/01.png", "images/practice/painting/02.png", "images/practice/painting/03.png", "images/practice/painting/04.png", "images/practice/painting/05.png", "images/practice/painting/06.png", "images/practice/painting/07.png", "images/practice/painting/08.png", "images/practice/painting/09.png", "images/practice/painting/10.png", "images/practice/painting/11.png", "images/practice/painting/12.png", "images/practice/painting/13.png", "images/practice/painting/14.png", "images/practice/painting/15.png", "images/practice/painting/16.png", "images/practice/painting/an_impasto_oil_painting_palette_knife_still_life.png", "images/practice/painting/an_impressionistic_oil_painting_style_scene_thick.png", "images/practice/painting/contemplative_ink_wash_portrait.png", "images/practice/painting/dramatic_monochrome_bearded_portrait.png", "images/practice/painting/impressionist_seaside_with_sail_tower.png", "images/practice/painting/kindly_elder_in_impasto_oils.png", "images/practice/painting/warm_watercolor_portrait_of_an_elderly_man.png", "images/practice/painting/watercolor_portrait_of_a_bearded_scholar.png", "images/practice/painting/watercolor_portrait_of_a_smiling_girl.png"], "photography": ["images/practice/photography/01.jpeg", "images/practice/photography/02.jpg", "images/practice/photography/03.jpg", "images/practice/photography/04.jpg", "images/practice/photography/05.jpg", "images/practice/photography/06.jpg", "images/practice/photography/07.jpg", "images/practice/photography/08.jpg", "images/practice/photography/09.jpg", "images/practice/photography/10.jpg", "images/practice/photography/11.jpg", "images/practice/photography/12.jpg", "images/practice/photography/13.jpg", "images/practice/photography/14.jpg", "images/practice/photography/15.jpg", "images/practice/photography/16.jpeg", "images/practice/photography/17.jpeg", "images/practice/photography/18.jpeg", "images/practice/photography/19.jpeg", "images/practice/photography/20.jpeg", "images/practice/photography/21.jpeg", "images/practice/photography/22.jpeg", "images/practice/photography/23.jpeg", "images/practice/photography/24.jpeg", "images/practice/photography/25.jpeg"], "graphic": ["images/practice/graphic/0ea3fa89-b719-40a0-bd37-df663a2dc50c.png", "images/practice/graphic/26594ad7-fa53-41e9-a4a7-b913fc515e30.png", "images/practice/graphic/733c36aa-bfff-4081-8a8a-310a2c846985.png", "images/practice/graphic/a_high_resolution_portrait_illustration_in_a_warm.png", "images/practice/graphic/cc637936-32c3-4ac1-939a-7ad2967c8ea8.png", "images/practice/graphic/d45df67a-325e-4a61-bdbd-bb0257448a5e.png"], "animation": ["images/practice/animation/2425899-walkcycle_side1(1).jpeg", "images/practice/animation/Horse runing.webp", "images/practice/animation/Hourse walk.gif", "images/practice/animation/Jump(1).png", "images/practice/animation/richard-williams-run-cycle-copy.jpg", "images/practice/animation/walk_cycle(1).jpg"], "education": ["images/education/01-capsat-exhibition.jpg", "images/education/02-media-exhibition.jpg", "images/education/03-adms-training.jpg", "images/education/04-adms-certificate.jpg", "images/education/05-adms-group.jpg", "images/education/06-training-2004.jpg", "images/education/07-training-2005.jpg", "images/education/08-adobe-workshop.jpg", "images/education/09-after-effects-class.jpg", "images/education/10-one-to-one-training.jpg", "images/education/11-event-demo.jpg", "images/education/12-training-session.jpg", "images/education/13-aramco-training.jpg", "images/education/14-training-group-modern.jpg", "images/education/15-class-selfie.jpg", "images/education/16-workshop-collaboration.jpg", "images/education/17-training-group.jpg", "images/education/18-lab-session.jpg", "images/education/19-adobe-session.jpg"]};
  const names={architecture:'Engineering',painting:'Painting & Digital Painting',photography:'Photography',graphic:'Graphic Design',animation:'Animation',education:'Training'};
  const grid=document.getElementById('bridgeGrid'); if(!grid) return;
  const buttons=[...document.querySelectorAll('[data-gallery-category]')];
  const title=document.getElementById('bridgeCategoryTitle'), count=document.getElementById('bridgeCount'), shuffle=document.getElementById('bridgeShuffle');
  const lightbox=document.getElementById('practiceLightbox'), lbImg=document.getElementById('practiceLightboxImage'), lbCap=document.getElementById('practiceLightboxCaption');
  let current='architecture', currentItems=[], currentIndex=0;
  function shuffled(a){a=[...a];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
  function render(cat, random=false){current=cat;buttons.forEach(b=>b.classList.toggle('is-active',b.dataset.galleryCategory===cat));if(title) title.textContent=names[cat];grid.innerHTML='';
    let items=random?shuffled(pools[cat]||[]):[...(pools[cat]||[])]; currentItems=items;
    if(cat==='animation'){
      items.forEach((src,i)=>{const b=document.createElement('button');b.className='bridge-item'+(i%7===0?' wide':'');b.innerHTML=`<img src="${src}" alt="Animation study ${i+1}" loading="lazy"><span class="item-index">${String(i+1).padStart(2,'0')}</span>`;b.addEventListener('click',()=>openLb(i));grid.appendChild(b)});
    } else {
      items.forEach((src,i)=>{const b=document.createElement('button');b.className='bridge-item'+(i%11===0?' wide':i%5===0?' tall':'');b.innerHTML=`<img src="${src}" alt="${names[cat]} work ${i+1}" loading="lazy"><span class="item-index">${String(i+1).padStart(2,'0')}</span>`;b.addEventListener('click',()=>openLb(i));grid.appendChild(b)});
    }
    count.textContent=`${items.length} items`;
  }
  function openLb(i){if(!currentItems.length)return;currentIndex=(i+currentItems.length)%currentItems.length;lbImg.src=hmImageVariant(currentItems[currentIndex],'previews');lbCap.textContent=`${names[current]} · ${String(currentIndex+1).padStart(2,'0')} / ${String(currentItems.length).padStart(2,'0')}`;lightbox.classList.add('is-open');lightbox.setAttribute('aria-hidden','false');document.body.style.overflow='hidden'}
  function closeLb(){lightbox.classList.remove('is-open');lightbox.setAttribute('aria-hidden','true');document.body.style.overflow=''}
  buttons.forEach(b=>b.addEventListener('click',()=>render(b.dataset.galleryCategory)));
  shuffle?.addEventListener('click',()=>render(current,true));
  document.getElementById('practiceLightboxClose')?.addEventListener('click',closeLb);
  document.getElementById('practiceLightboxPrev')?.addEventListener('click',()=>openLb(currentIndex-1));
  document.getElementById('practiceLightboxNext')?.addEventListener('click',()=>openLb(currentIndex+1));
  lightbox?.addEventListener('click',e=>{if(e.target===lightbox)closeLb()});
  window.addEventListener('keydown',e=>{if(!lightbox?.classList.contains('is-open'))return;if(e.key==='Escape')closeLb();if(e.key==='ArrowLeft')openLb(currentIndex-1);if(e.key==='ArrowRight')openLb(currentIndex+1)});
  render('architecture');
})();

(() => {
  const stack=document.getElementById('knowledgeStack'); if(!stack) return;
  stack.addEventListener('click',e=>{const card=e.target.closest('[data-kcard]');if(!card)return;card.classList.add('is-flipping');setTimeout(()=>{stack.appendChild(card);card.classList.remove('is-flipping')},520)});
})();


/* v1.26 — Selected Work lightbox */
(() => {
  const lb=document.getElementById('selectedWorkLightbox'); if(!lb)return;
  const img=lb.querySelector('img'), close=lb.querySelector('button');
  document.querySelectorAll('[data-selected-src]').forEach(b=>b.addEventListener('click',()=>{img.src=b.dataset.selectedSrc;lb.classList.add('is-open');lb.setAttribute('aria-hidden','false');document.body.style.overflow='hidden'}));
  const shut=()=>{lb.classList.remove('is-open');lb.setAttribute('aria-hidden','true');document.body.style.overflow=''};
  close.addEventListener('click',shut);lb.addEventListener('click',e=>{if(e.target===lb)shut()});window.addEventListener('keydown',e=>{if(e.key==='Escape'&&lb.classList.contains('is-open'))shut()});
})();

/* HM FINAL — Chronological Life Timeline */
(() => {
  const strip = document.getElementById('lifeStrip');
  if (!strip) return;

  const indicator = document.getElementById('lifeTimelineIndicator');
  const lightbox = document.getElementById('lifeLightbox');
  const lightboxImage = document.getElementById('lifeLightboxImage');
  const lightboxCounter = document.getElementById('lifeLightboxCounter');
  const lightboxDate = document.getElementById('lifeLightboxDate');
  const lightboxCaption = document.getElementById('lifeLightboxCaption');
  const closeLightbox = document.getElementById('lifeLightboxClose');
  const prevLightbox = document.getElementById('lifeLightboxPrev');
  const nextLightbox = document.getElementById('lifeLightboxNext');

  const editorModal = document.getElementById('lifeEditorModal');
  const editorForm = document.getElementById('lifeEditorForm');
  const editorDate = document.getElementById('lifeEditorDate');
  const editorCaption = document.getElementById('lifeEditorCaption');
  const editorError = document.getElementById('lifeEditorError');
  const editorClose = document.getElementById('lifeEditorClose');
  const editorCancel = document.getElementById('lifeEditorCancel');

  const editMode =
    (location.hostname === '127.0.0.1' || location.hostname === 'localhost') &&
    new URLSearchParams(location.search).get('timeline-edit') === '1';

  document.documentElement.classList.toggle('timeline-edit-mode', editMode);

  const pad = n => String(n).padStart(2, '0');

  const fileFromSrc = src => {
    const clean = String(src || '').split('?')[0].split('#')[0];
    return decodeURIComponent(clean.substring(clean.lastIndexOf('/') + 1));
  };

  const toPreview = src => String(src || '').replace('/thumbs/', '/previews/');

  const validDate = value =>
    value === '' ||
    /^\d{4}$/.test(value) ||
    /^\d{4}-(0[1-9]|1[0-2])$/.test(value) ||
    /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/.test(value);

  const dateKey = value => {
    const v = String(value || '').trim();
    if (!validDate(v) || !v) return Number.POSITIVE_INFINITY;
    const parts = v.split('-').map(Number);
    const y = parts[0];
    const m = parts[1] || 0;
    const d = parts[2] || 0;
    return (y * 10000) + (m * 100) + d;
  };

  const sourceData = Array.isArray(window.HM_LIFE_TIMELINE)
    ? window.HM_LIFE_TIMELINE
    : [];

  const metadata = new Map(
    sourceData
      .filter(item => item && item.file)
      .map(item => [
        String(item.file),
        {
          file: String(item.file),
          date: String(item.date || '').trim(),
          caption: String(item.caption || '').trim()
        }
      ])
  );

  let thumbs = [];
  let index = 0;
  let editingFile = null;

  function ensureCardParts(thumb, originalOrder) {
    const img = thumb.querySelector('img');
    if (!img) return;

    const file = fileFromSrc(img.getAttribute('src') || img.currentSrc || img.src);
    thumb.dataset.lifeFile = file;
    thumb.dataset.originalOrder = String(originalOrder);

    let track = thumb.querySelector('.life-thumb-track');
    if (!track) {
      track = document.createElement('span');
      track.className = 'life-thumb-track';
      track.innerHTML = '<span class="life-thumb-dot"></span>';
      thumb.prepend(track);
    }

    let body = thumb.querySelector('.life-thumb-body');
    if (!body) {
      body = document.createElement('span');
      body.className = 'life-thumb-body';
      img.replaceWith(body);
      body.appendChild(img);
    }

    let meta = thumb.querySelector('.life-thumb-meta');
    if (!meta) {
      meta = document.createElement('span');
      meta.className = 'life-thumb-meta';
      meta.innerHTML = `
        <span class="life-thumb-date"></span>
        <span class="life-thumb-caption"></span>
      `;
      thumb.appendChild(meta);
    }

    if (editMode && !thumb.querySelector('.life-thumb-settings')) {
      const settings = document.createElement('span');
      settings.className = 'life-thumb-settings';
      settings.setAttribute('role', 'button');
      settings.setAttribute('aria-label', 'Edit date and caption');
      settings.title = 'Edit date and caption';
      settings.innerHTML = `
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 7h10M18 7h2M4 17h2M10 17h10M8 4v6M16 14v6"></path>
        </svg>
      `;
      body.appendChild(settings);
    }
  }

  function getMeta(thumb) {
    const file = thumb.dataset.lifeFile || '';
    return metadata.get(file) || { file, date: '', caption: '' };
  }

  function refreshCard(thumb) {
    const meta = getMeta(thumb);
    const dateEl = thumb.querySelector('.life-thumb-date');
    const captionEl = thumb.querySelector('.life-thumb-caption');
    if (dateEl) {
      dateEl.textContent = meta.date || 'Undated';
      dateEl.classList.toggle('is-undated', !meta.date);
    }
    if (captionEl) {
      captionEl.textContent = meta.caption || '';
      captionEl.classList.toggle('is-empty', !meta.caption);
    }
  }

  function sortTimeline(selectedFile = null) {
    thumbs = [...strip.querySelectorAll('.life-thumb')];
    thumbs.sort((a, b) => {
      const ka = dateKey(getMeta(a).date);
      const kb = dateKey(getMeta(b).date);
      if (ka !== kb) return ka - kb;
      return Number(a.dataset.originalOrder || 0) - Number(b.dataset.originalOrder || 0);
    });
    thumbs.forEach(thumb => strip.appendChild(thumb));
    thumbs.forEach(refreshCard);
    if (selectedFile) {
      const found = thumbs.findIndex(t => t.dataset.lifeFile === selectedFile);
      index = found >= 0 ? found : 0;
    } else {
      index = Math.max(0, Math.min(index, thumbs.length - 1));
    }
    syncSelection(false);
  }

  function moveIndicator(thumb) {
    if (!indicator || !thumb) return;
    const x = thumb.offsetLeft + (thumb.offsetWidth / 2);
    indicator.style.transform = `translateX(${x}px)`;
  }

  function syncSelection(scrollIntoView = true) {
    if (!thumbs.length) return;
    thumbs.forEach((thumb, i) => {
      const active = i === index;
      thumb.classList.toggle('is-active', active);
      thumb.setAttribute('aria-current', active ? 'true' : 'false');
    });
    const thumb = thumbs[index];
    moveIndicator(thumb);
    if (scrollIntoView) {
      thumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      setTimeout(() => moveIndicator(thumb), 320);
    }
  }

  function openImage(nextIndex) {
    if (!thumbs.length || !lightbox || !lightboxImage) return;
    index = (nextIndex + thumbs.length) % thumbs.length;
    syncSelection(true);
    const thumb = thumbs[index];
    const img = thumb.querySelector('img');
    const meta = getMeta(thumb);
    const rawSrc = img?.getAttribute('src') || img?.currentSrc || img?.src || '';
    lightboxImage.src = toPreview(rawSrc);
    lightboxImage.alt = img?.alt || `Life timeline photograph ${index + 1}`;
    if (lightboxCounter) lightboxCounter.textContent = `${pad(index + 1)} / ${pad(thumbs.length)}`;
    if (lightboxDate) lightboxDate.textContent = meta.date || 'Undated';
    if (lightboxCaption) lightboxCaption.textContent = meta.caption || '';
    lightbox.classList.add('is-open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeImage() {
    if (!lightbox) return;
    lightbox.classList.remove('is-open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  function openEditor(thumb) {
    if (!editMode || !editorModal) return;
    const meta = getMeta(thumb);
    editingFile = thumb.dataset.lifeFile;
    editorDate.value = meta.date || '';
    editorCaption.value = meta.caption || '';
    editorError.hidden = true;
    editorError.textContent = '';
    editorModal.classList.add('is-open');
    editorModal.setAttribute('aria-hidden', 'false');
    setTimeout(() => editorDate.focus(), 30);
  }

  function closeEditor() {
    if (!editorModal) return;
    editorModal.classList.remove('is-open');
    editorModal.setAttribute('aria-hidden', 'true');
    editingFile = null;
  }

  async function saveEditor(event) {
    event.preventDefault();
    if (!editingFile) return;
    const date = editorDate.value.trim();
    const caption = editorCaption.value.trim();
    if (!validDate(date)) {
      editorError.textContent = 'Use YYYY, YYYY-MM, or YYYY-MM-DD.';
      editorError.hidden = false;
      editorDate.focus();
      return;
    }
    metadata.set(editingFile, { file: editingFile, date, caption });
    const payload = [...metadata.values()];
    try {
      const response = await fetch('/api/timeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error(await response.text());
      closeEditor();
      sortTimeline(editingFile);
    } catch (error) {
      editorError.textContent = 'Could not save. Open the site using EDIT_TIMELINE.bat.';
      editorError.hidden = false;
      console.error(error);
    }
  }

  [...strip.querySelectorAll('.life-thumb')].forEach((thumb, i) => ensureCardParts(thumb, i));
  thumbs = [...strip.querySelectorAll('.life-thumb')];
  sortTimeline();

  let dragged = false;
  strip.addEventListener('click', event => {
    const thumb = event.target.closest('.life-thumb');
    if (!thumb || !strip.contains(thumb)) return;
    if (dragged || strip.dataset.wasDragged === 'true') return;
    const settings = event.target.closest('.life-thumb-settings');
    if (settings) {
      event.preventDefault();
      event.stopPropagation();
      openEditor(thumb);
      return;
    }
    event.preventDefault();
    const i = thumbs.indexOf(thumb);
    if (i >= 0) openImage(i);
  });

  closeLightbox?.addEventListener('click', closeImage);
  prevLightbox?.addEventListener('click', event => { event.stopPropagation(); openImage(index - 1); });
  nextLightbox?.addEventListener('click', event => { event.stopPropagation(); openImage(index + 1); });
  lightbox?.addEventListener('click', event => { if (event.target === lightbox) closeImage(); });

  editorForm?.addEventListener('submit', saveEditor);
  editorClose?.addEventListener('click', closeEditor);
  editorCancel?.addEventListener('click', closeEditor);
  editorModal?.addEventListener('click', event => { if (event.target === editorModal) closeEditor(); });

  window.addEventListener('keydown', event => {
    if (editorModal?.classList.contains('is-open')) {
      if (event.key === 'Escape') closeEditor();
      return;
    }
    if (!lightbox?.classList.contains('is-open')) return;
    if (event.key === 'Escape') closeImage();
    if (event.key === 'ArrowLeft') openImage(index - 1);
    if (event.key === 'ArrowRight') openImage(index + 1);
  });

  let dragging = false;
  let startX = 0;
  let startScroll = 0;
  strip.addEventListener('pointerdown', event => {
    if (event.button !== undefined && event.button !== 0) return;
    dragging = true;
    dragged = false;
    strip.dataset.wasDragged = 'false';
    startX = event.clientX;
    startScroll = strip.scrollLeft;
  });
  window.addEventListener('pointermove', event => {
    if (!dragging) return;
    const dx = event.clientX - startX;
    if (!dragged && Math.abs(dx) > 7) {
      dragged = true;
      strip.dataset.wasDragged = 'true';
      strip.classList.add('is-dragging');
    }
    if (dragged) {
      strip.scrollLeft = startScroll - dx;
      event.preventDefault();
    }
  }, { passive: false });
  window.addEventListener('pointerup', () => {
    if (!dragging) return;
    dragging = false;
    strip.classList.remove('is-dragging');
    setTimeout(() => { dragged = false; strip.dataset.wasDragged = 'false'; }, 90);
  });
  window.addEventListener('pointercancel', () => {
    dragging = false;
    dragged = false;
    strip.classList.remove('is-dragging');
    strip.dataset.wasDragged = 'false';
  });
  window.addEventListener('resize', () => { if (thumbs[index]) moveIndicator(thumbs[index]); });
})();

/* HM PATCH — Selected Work navigator */
(() => {
  const items=[...document.querySelectorAll('.selected-work-item')];
  const lb=document.getElementById('selectedWorkLightbox');
  if(!items.length||!lb)return;
  const img=document.getElementById('selectedWorkLightboxImage')||lb.querySelector('img');
  const close=document.getElementById('selectedWorkClose')||lb.querySelector('button');
  let index=0;
  const srcFor=item=>item.dataset.selectedSrc||item.querySelector('img')?.src;
  function show(i){
    index=(i+items.length)%items.length;
    if(img){img.src=srcFor(items[index]);img.alt=items[index].querySelector('img')?.alt||'Selected portfolio work';}
  }
  function open(i){show(i);lb.classList.add('is-open');lb.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';}
  function shut(){lb.classList.remove('is-open');lb.setAttribute('aria-hidden','true');document.body.style.overflow='';}
  items.forEach((item,i)=>item.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();open(i);},true));
  document.getElementById('selectedWorkPrev')?.addEventListener('click',e=>{e.stopPropagation();show(index-1);});
  document.getElementById('selectedWorkNext')?.addEventListener('click',e=>{e.stopPropagation();show(index+1);});
  close?.addEventListener('click',e=>{e.stopPropagation();shut();});
  lb.addEventListener('click',e=>{if(e.target===lb)shut();});
  window.addEventListener('keydown',e=>{
    if(!lb.classList.contains('is-open'))return;
    if(e.key==='Escape')shut();
    if(e.key==='ArrowLeft')show(index-1);
    if(e.key==='ArrowRight')show(index+1);
  });
})();

/* HM PATCH — Knowledge gallery */
(() => {
  const items=[...document.querySelectorAll('.knowledge-gallery-item')];
  const lb=document.getElementById('knowledgeLightbox');
  const img=document.getElementById('knowledgeLightboxImage');
  const cap=document.getElementById('knowledgeLightboxCaption');
  if(!items.length||!lb||!img)return;
  let index=0;
  function show(i){
    index=(i+items.length)%items.length;
    const source=items[index].querySelector('img');
    const title=items[index].querySelector('span')?.textContent||`Knowledge item ${index+1}`;
    img.src=(source.currentSrc||source.src).replace('/thumbs/','/previews/');
    img.alt=source.alt||title;
    if(cap)cap.textContent=`${title} · ${String(index+1).padStart(2,'0')} / ${String(items.length).padStart(2,'0')}`;
  }
  function open(i){show(i);lb.classList.add('is-open');lb.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';}
  function close(){lb.classList.remove('is-open');lb.setAttribute('aria-hidden','true');document.body.style.overflow='';}
  items.forEach((item,i)=>item.addEventListener('click',()=>open(i)));
  document.getElementById('knowledgePrev')?.addEventListener('click',e=>{e.stopPropagation();show(index-1);});
  document.getElementById('knowledgeNext')?.addEventListener('click',e=>{e.stopPropagation();show(index+1);});
  document.getElementById('knowledgeClose')?.addEventListener('click',close);
  lb.addEventListener('click',e=>{if(e.target===lb)close();});
  window.addEventListener('keydown',e=>{
    if(!lb.classList.contains('is-open'))return;
    if(e.key==='Escape')close();
    if(e.key==='ArrowLeft')show(index-1);
    if(e.key==='ArrowRight')show(index+1);
  });
})();


/* HM FINAL — Knowledge categories + lightbox */
(() => {
  const allItems=[...document.querySelectorAll('.knowledge-thumb')];
  const buttons=[...document.querySelectorAll('[data-knowledge-filter]')];
  const title=document.getElementById('knowledgeCategoryTitle');
  const count=document.getElementById('knowledgeCount');
  const empty=document.getElementById('knowledgeEmpty');
  const lb=document.getElementById('knowledgeLightbox');
  const lbImg=document.getElementById('knowledgeLightboxImage');
  const lbCap=document.getElementById('knowledgeLightboxCaption');
  if(!allItems.length || !buttons.length || !lb || !lbImg) return;
  const labels={engineering:'Engineering',painting:'Painting & Digital Painting',photography:'Photography',graphic:'Graphic Design',animation:'Animation',training:'Training'};
  let currentCategory='engineering', currentItems=[], index=0;
  const toPreview=src=>(src||'').replace('/thumbs/','/previews/');
  function render(cat){
    currentCategory=cat; currentItems=allItems.filter(i=>i.dataset.knowledgeCategory===cat);
    allItems.forEach(i=>i.hidden=i.dataset.knowledgeCategory!==cat);
    buttons.forEach(b=>b.classList.toggle('is-active',b.dataset.knowledgeFilter===cat));
    if(title) title.textContent=labels[cat];
    if(count) count.textContent=`${currentItems.length} items`;
    if(empty) empty.hidden=currentItems.length!==0;
  }
  function show(i){
    if(!currentItems.length) return; index=(i+currentItems.length)%currentItems.length;
    const t=currentItems[index].querySelector('img');
    lbImg.src=toPreview(t.currentSrc||t.src); lbImg.alt=t.alt||labels[currentCategory];
    if(lbCap) lbCap.textContent=`${labels[currentCategory]} · ${String(index+1).padStart(2,'0')} / ${String(currentItems.length).padStart(2,'0')}`;
  }
  function open(item){ const i=currentItems.indexOf(item); if(i<0)return; show(i); lb.classList.add('is-open'); lb.setAttribute('aria-hidden','false'); document.body.style.overflow='hidden'; }
  function close(){ lb.classList.remove('is-open'); lb.setAttribute('aria-hidden','true'); document.body.style.overflow=''; }
  buttons.forEach(b=>b.addEventListener('click',()=>render(b.dataset.knowledgeFilter)));
  allItems.forEach(item=>item.addEventListener('click',()=>open(item)));
  document.getElementById('knowledgePrev')?.addEventListener('click',e=>{e.stopPropagation();show(index-1);});
  document.getElementById('knowledgeNext')?.addEventListener('click',e=>{e.stopPropagation();show(index+1);});
  document.getElementById('knowledgeClose')?.addEventListener('click',close);
  lb.addEventListener('click',e=>{if(e.target===lb)close();});
  window.addEventListener('keydown',e=>{if(!lb.classList.contains('is-open'))return;if(e.key==='Escape')close();if(e.key==='ArrowLeft')show(index-1);if(e.key==='ArrowRight')show(index+1);});
  render('engineering');
})();
