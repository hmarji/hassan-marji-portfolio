from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
CSS = ROOT / "css" / "style.css"
MANAGER = ROOT / "js" / "gallery-manager.js"

for p in (HTML, CSS, MANAGER):
    if not p.exists():
        raise SystemExit(f"ERROR: Missing {p}. Put this patch directly in the portfolio root folder.")

html = HTML.read_text(encoding="utf-8")
css = CSS.read_text(encoding="utf-8")
manager = MANAGER.read_text(encoding="utf-8")

m = re.search(r'<section class="knowledge[^\"]*" id="knowledge">.*?</section>', html, re.S)
if not m:
    raise SystemExit("ERROR: Knowledge section not found.")

knowledge = '''
<section class="practice practice-gallery knowledge-practice" id="knowledge">
  <div class="practice-heading practice-heading-gallery">
    <p class="section-index">03 / Knowledge</p>
    <div><h2>Knowledge in visual form.</h2></div>
  </div>

  <div class="bridge-browser knowledge-browser">
    <aside class="bridge-sidebar knowledge-sidebar" aria-label="Knowledge categories">
      <p class="bridge-label">Collections</p>
      <button class="bridge-category knowledge-category is-active" data-knowledge-filter="engineering"><span>01</span>Engineering</button>
      <button class="bridge-category knowledge-category" data-knowledge-filter="painting"><span>02</span>Painting &amp; Digital Painting</button>
      <button class="bridge-category knowledge-category" data-knowledge-filter="photography"><span>03</span>Photography</button>
      <button class="bridge-category knowledge-category" data-knowledge-filter="graphic"><span>04</span>Graphic Design</button>
      <button class="bridge-category knowledge-category" data-knowledge-filter="animation"><span>05</span>Animation</button>
      <button class="bridge-category knowledge-category" data-knowledge-filter="training"><span>06</span>Training</button>
    </aside>

    <div class="bridge-content knowledge-content">
      <div class="bridge-toolbar knowledge-toolbar">
        <div>
          <h3 id="knowledgeCategoryTitle">Engineering</h3>
          <small id="knowledgeCount"></small>
        </div>
        <button id="knowledgeShuffle" type="button">Shuffle</button>
      </div>

      <div class="knowledge-gallery-grid" id="knowledgeGallery" aria-live="polite"></div>
      <p class="knowledge-empty" id="knowledgeEmpty" hidden>No items in this category yet.</p>
    </div>
  </div>

  <div class="knowledge-lightbox" id="knowledgeLightbox" aria-hidden="true">
    <button class="knowledge-lightbox-close" id="knowledgeClose" type="button" aria-label="Close knowledge item">×</button>
    <button class="knowledge-lightbox-nav prev" id="knowledgePrev" type="button" aria-label="Previous knowledge item">←</button>
    <figure><img id="knowledgeLightboxImage" alt="Knowledge item"><figcaption id="knowledgeLightboxCaption"></figcaption></figure>
    <button class="knowledge-lightbox-nav next" id="knowledgeNext" type="button" aria-label="Next knowledge item">→</button>
  </div>
</section>
'''

html = html[:m.start()] + knowledge + html[m.end():]

for marker in [
    "/* HM FINAL - Knowledge visually matches Practice */",
    "/* HM FINAL — Knowledge visually matches Practice */",
    "/* HM FINAL - Knowledge uses the exact Practice layout */",
]:
    pos = css.find(marker)
    if pos != -1:
        css = css[:pos].rstrip() + "\n"

css += r'''

/* HM KNOWLEDGE V2 - exact Practice page structure */
.knowledge-practice .practice-heading-gallery{
  margin-bottom:0 !important;
}

.knowledge-practice .knowledge-gallery-grid{
  display:grid !important;
  grid-template-columns:repeat(4,minmax(0,1fr)) !important;
  gap:10px !important;
  align-items:start !important;
}

.knowledge-practice .knowledge-thumb{
  position:relative !important;
  aspect-ratio:16 / 9 !important;
  border:0 !important;
  padding:0 !important;
  overflow:hidden !important;
  background:#111 !important;
  cursor:zoom-in !important;
}

.knowledge-practice .knowledge-thumb img{
  display:block !important;
  width:100% !important;
  height:100% !important;
  object-fit:cover !important;
  transition:transform .28s ease, filter .28s ease !important;
}

.knowledge-practice .knowledge-thumb:hover img{
  transform:scale(1.025) !important;
}

.knowledge-practice .knowledge-thumb-index{
  position:absolute !important;
  left:6px !important;
  bottom:6px !important;
  padding:2px 5px !important;
  background:rgba(0,0,0,.65) !important;
  color:#ddd !important;
  font-size:9px !important;
  letter-spacing:.1em !important;
}

.knowledge-practice .knowledge-empty{
  color:#777 !important;
  font-size:12px !important;
  padding:22px 0 !important;
}

.knowledge-practice .practice-heading-gallery h2{
  white-space:nowrap !important;
  font-size:clamp(24px,2.25vw,42px) !important;
  line-height:1.05 !important;
}

@media(max-width:1100px){
  .knowledge-practice .knowledge-gallery-grid{
    grid-template-columns:repeat(3,minmax(0,1fr)) !important;
  }
}

@media(max-width:760px){
  .knowledge-practice .practice-heading-gallery h2{
    white-space:normal !important;
  }
  .knowledge-practice .knowledge-gallery-grid{
    grid-template-columns:repeat(2,minmax(0,1fr)) !important;
  }
}

@media(max-width:520px){
  .knowledge-practice .knowledge-gallery-grid{
    grid-template-columns:1fr !important;
  }
}
'''

if "const shuffle = document.getElementById('knowledgeShuffle');" not in manager:
    manager = manager.replace(
        "const empty = document.getElementById('knowledgeEmpty');",
        "const empty = document.getElementById('knowledgeEmpty');\n    const shuffle = document.getElementById('knowledgeShuffle');"
    )

if "shuffle?.addEventListener('click'" not in manager:
    manager = manager.replace(
        "buttons.forEach(b => b.addEventListener('click', () => render(b.dataset.knowledgeFilter)));",
        """buttons.forEach(b => b.addEventListener('click', () => render(b.dataset.knowledgeFilter)));\n    shuffle?.addEventListener('click', () => {\n      const arr = categories[current] || [];\n      for (let i = arr.length - 1; i > 0; i--) {\n        const j = Math.floor(Math.random() * (i + 1));\n        [arr[i], arr[j]] = [arr[j], arr[i]];\n      }\n      render(current);\n    });"""
    )

HTML.write_text(html, encoding="utf-8")
CSS.write_text(css, encoding="utf-8")
MANAGER.write_text(manager, encoding="utf-8")

print("SUCCESS - Knowledge now uses the same page structure as Practice.")
print("Title is at the top, Collections sidebar is below it, gallery is to the right.")
print("The large empty left area is removed.")
print("Knowledge keeps wide 16:9 thumbnails and has Shuffle.")
print("The folder-driven UPDATE_PORTFOLIO system remains unchanged.")
