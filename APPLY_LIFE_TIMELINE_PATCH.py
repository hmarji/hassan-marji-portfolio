from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
MAIN = ROOT / "js" / "main.js"
CSS = ROOT / "css" / "style.css"
DATA = ROOT / "js" / "life-timeline-data.js"

required = [INDEX, MAIN, CSS]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit(
        "ERROR: Put APPLY_LIFE_TIMELINE_PATCH.py and APPLY_LIFE_TIMELINE_PATCH.bat "
        "in the main HM Portfolio folder (same folder as index.html).\n"
        "Missing: " + ", ".join(missing)
    )

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = ROOT / f"_backup_life_timeline_{stamp}"
backup.mkdir(exist_ok=True)

for p in required:
    dest = backup / p.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)

if DATA.exists():
    dest = backup / DATA.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATA, dest)

# 1) Editable timeline metadata, matched by filename.
if not DATA.exists():
    entries = []
    for n in range(21, 40):
        entries.append(f'  {{ file: "{n}.webp", date: "", caption: "" }}')

    data_text = """/* HM Portfolio — Life Timeline metadata
Edit only the date and caption values below.

Examples:
  date: "1978"
  date: "June 1996"
  caption: "At school in Beirut."

The file name identifies the photograph, so you can reorder thumbnails
without losing the correct date/caption.
*/
window.HM_LIFE_TIMELINE = [
%s
];
""" % (",\n".join(entries))

    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(data_text, encoding="utf-8")

# 2) Load metadata BEFORE main.js.
html = INDEX.read_text(encoding="utf-8")

if 'js/life-timeline-data.js' not in html:
    marker = '<script src="js/main.js"></script>'
    if marker not in html:
        raise SystemExit("ERROR: Could not find the main.js script tag in index.html.")
    html = html.replace(
        marker,
        '<script src="js/life-timeline-data.js"></script>\n    ' + marker,
        1
    )

# 3) Add large date/caption area beside the main viewer image.
if 'id="lifeDate"' not in html:
    old_figure_re = re.compile(
        r'<figure>\s*'
        r'(<img\s+id="lifeMainImage"[^>]*>)\s*'
        r'<figcaption>\s*'
        r'(<span\s+id="lifeCounter"[^>]*>.*?</span>)\s*'
        r'</figcaption>\s*</figure>',
        re.S
    )

    m = old_figure_re.search(html)
    if not m:
        raise SystemExit("ERROR: Could not find the Life Timeline viewer figure in index.html.")

    new_figure = """<figure>
            %s
            <figcaption class="life-viewer-meta">
              %s
              <div class="life-viewer-date">
                <span class="life-meta-label">Date</span>
                <strong id="lifeDate">—</strong>
              </div>
              <div class="life-viewer-caption">
                <span class="life-meta-label">Caption</span>
                <p id="lifeCaption">Life timeline photograph 01</p>
              </div>
            </figcaption>
          </figure>""" % (m.group(1), m.group(2))

    html = html[:m.start()] + new_figure + html[m.end():]

INDEX.write_text(html, encoding="utf-8")

# 4) Replace BOTH old/duplicate timeline controllers with ONE robust controller.
js = MAIN.read_text(encoding="utf-8")

start_marker = "/* v1.26 — edge-to-edge Life Timeline navigator */"
end_marker = "/* HM PATCH — Selected Work navigator */"

start = js.find(start_marker)
end = js.find(end_marker)

if start < 0 or end < 0 or end <= start:
    raise SystemExit(
        "ERROR: Could not locate the current Life Timeline controller in js/main.js. "
        "No changes were made to main.js."
    )

new_controller = r"""/* HM FINAL — Life Timeline viewer + date/caption metadata */
(() => {
  const strip = document.getElementById('lifeStrip');
  const main = document.getElementById('lifeMainImage');
  const counter = document.getElementById('lifeCounter');
  const dateEl = document.getElementById('lifeDate');
  const captionEl = document.getElementById('lifeCaption');
  const prev = document.getElementById('lifePrev');
  const next = document.getElementById('lifeNext');

  if (!strip || !main) return;

  const thumbs = [...strip.querySelectorAll('.life-thumb')];
  if (!thumbs.length) return;

  const metadata = Array.isArray(window.HM_LIFE_TIMELINE)
    ? window.HM_LIFE_TIMELINE
    : [];

  const metaByFile = new Map(
    metadata
      .filter(item => item && item.file)
      .map(item => [String(item.file).toLowerCase(), item])
  );

  const pad = n => String(n).padStart(2, '0');

  const fileFromSrc = src => {
    const clean = String(src || '').split('?')[0].split('#')[0];
    return decodeURIComponent(clean.substring(clean.lastIndexOf('/') + 1)).toLowerCase();
  };

  const toPreview = src => String(src || '').replace('/thumbs/', '/previews/');

  const getMeta = (thumb, i) => {
    const img = thumb.querySelector('img');
    const file = fileFromSrc(img?.getAttribute('src') || img?.currentSrc || img?.src);
    const item = metaByFile.get(file) || {};
    return {
      date: String(item.date || '').trim(),
      caption: String(item.caption || '').trim(),
      fallbackCaption: `Life timeline photograph ${pad(i + 1)}`
    };
  };

  // Add compact date + caption underneath every thumbnail.
  thumbs.forEach((thumb, i) => {
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

    const item = getMeta(thumb, i);
    meta.querySelector('.life-thumb-date').textContent = item.date || '—';
    meta.querySelector('.life-thumb-caption').textContent =
      item.caption || item.fallbackCaption;
  });

  let index = Math.max(
    0,
    thumbs.findIndex(thumb => thumb.classList.contains('is-active'))
  );

  function show(nextIndex, scrollThumb = true) {
    index = (nextIndex + thumbs.length) % thumbs.length;

    thumbs.forEach((thumb, i) => {
      const active = i === index;
      thumb.classList.toggle('is-active', active);
      thumb.setAttribute('aria-current', active ? 'true' : 'false');
    });

    const thumb = thumbs[index];
    const img = thumb.querySelector('img');

    if (img) {
      const rawSrc = img.getAttribute('src') || img.currentSrc || img.src;
      main.src = toPreview(rawSrc);
      main.alt = img.alt || `Life timeline photograph ${index + 1}`;
    }

    if (counter) {
      counter.textContent = `${pad(index + 1)} / ${pad(thumbs.length)}`;
    }

    const item = getMeta(thumb, index);
    if (dateEl) dateEl.textContent = item.date || '—';
    if (captionEl) captionEl.textContent = item.caption || item.fallbackCaption;

    if (scrollThumb) {
      thumb.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center'
      });
    }
  }

  // Reliable click selection using event delegation.
  strip.addEventListener('click', event => {
    const thumb = event.target.closest('.life-thumb');
    if (!thumb || !strip.contains(thumb)) return;
    if (strip.dataset.wasDragged === 'true') return;

    event.preventDefault();
    const i = thumbs.indexOf(thumb);
    if (i >= 0) show(i, false);
  });

  prev?.addEventListener('click', () => show(index - 1));
  next?.addEventListener('click', () => show(index + 1));

  // Drag horizontally WITHOUT pointer capture.
  // This is the key fix that keeps normal thumbnail clicks alive.
  let dragging = false;
  let moved = false;
  let startX = 0;
  let startScroll = 0;
  const dragThreshold = 7;

  strip.addEventListener('pointerdown', event => {
    if (event.button !== undefined && event.button !== 0) return;
    dragging = true;
    moved = false;
    strip.dataset.wasDragged = 'false';
    startX = event.clientX;
    startScroll = strip.scrollLeft;
  });

  window.addEventListener('pointermove', event => {
    if (!dragging) return;

    const dx = event.clientX - startX;

    if (!moved && Math.abs(dx) > dragThreshold) {
      moved = true;
      strip.classList.add('is-dragging');
      strip.dataset.wasDragged = 'true';
    }

    if (moved) {
      strip.scrollLeft = startScroll - dx;
      event.preventDefault();
    }
  }, { passive: false });

  window.addEventListener('pointerup', () => {
    if (!dragging) return;

    dragging = false;
    strip.classList.remove('is-dragging');

    setTimeout(() => {
      strip.dataset.wasDragged = 'false';
    }, 80);
  });

  window.addEventListener('pointercancel', () => {
    dragging = false;
    strip.classList.remove('is-dragging');
    strip.dataset.wasDragged = 'false';
  });

  show(index, false);
})();

"""

js = js[:start] + new_controller + js[end:]
MAIN.write_text(js, encoding="utf-8")

# 5) Styling for thumbnail metadata and the larger viewer metadata.
css = CSS.read_text(encoding="utf-8")

css_marker = "/* HM FINAL — Life Timeline metadata layout */"
css_patch = r"""/* HM FINAL — Life Timeline metadata layout */
.life-viewer figure {
  grid-template-columns: minmax(0, 1fr) clamp(210px, 22vw, 340px);
  gap: clamp(20px, 3vw, 48px);
  align-items: stretch;
}

.life-viewer figure > img {
  min-width: 0;
}

.life-viewer-meta {
  min-width: 0 !important;
  padding: 14px 0 10px;
  align-self: stretch;
  align-content: start;
  gap: 26px !important;
}

.life-viewer-meta #lifeCounter {
  color: var(--hm-orange);
}

.life-viewer-date,
.life-viewer-caption {
  display: grid;
  gap: 8px;
}

.life-meta-label {
  color: var(--hm-muted);
  font-size: 9px;
  font-weight: 500;
  letter-spacing: .16em;
  text-transform: uppercase;
}

.life-viewer-date strong {
  color: var(--hm-text);
  font-family: "Manrope", Arial, sans-serif;
  font-size: clamp(20px, 2vw, 32px);
  font-weight: 300;
  letter-spacing: -.035em;
  line-height: 1.05;
  text-transform: none;
}

.life-viewer-caption p {
  margin: 0;
  color: var(--hm-text);
  font-family: "Manrope", Arial, sans-serif;
  font-size: clamp(18px, 1.6vw, 28px);
  font-weight: 300;
  letter-spacing: -.025em;
  line-height: 1.2;
  text-transform: none;
}

.life-strip {
  align-items: stretch;
}

.life-thumb {
  height: auto !important;
  min-height: 0;
  display: grid;
  grid-template-rows: clamp(130px, 14vw, 220px) auto;
  align-content: start;
  overflow: hidden;
  opacity: .68;
  text-align: left;
}

.life-thumb img {
  width: 100%;
  height: 100% !important;
  min-height: 0;
  object-fit: cover;
}

.life-thumb-meta {
  min-height: 70px;
  padding: 9px 10px 12px;
  display: grid;
  align-content: start;
  gap: 5px;
  border-top: 1px solid var(--hm-line);
  background: #0d0d0d;
  pointer-events: none;
}

.life-thumb-date {
  color: var(--hm-orange);
  font-size: 8px;
  font-weight: 500;
  letter-spacing: .13em;
  line-height: 1.2;
  text-transform: uppercase;
}

.life-thumb-caption {
  color: var(--hm-text);
  font-size: 10px;
  font-weight: 300;
  letter-spacing: 0;
  line-height: 1.3;
  text-transform: none;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.life-strip.is-dragging {
  cursor: grabbing;
  user-select: none;
}

@media (max-width: 760px) {
  .life-viewer {
    grid-template-columns: 44px minmax(0, 1fr) 44px;
    gap: 8px;
  }

  .life-viewer figure {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .life-viewer-meta {
    padding-top: 0;
    gap: 16px !important;
  }

  .life-thumb-meta {
    min-height: 62px;
  }
}
"""

if css_marker in css:
    css = css[:css.index(css_marker)].rstrip() + "\n\n" + css_patch
else:
    css = css.rstrip() + "\n\n" + css_patch

CSS.write_text(css, encoding="utf-8")

print()
print("HM Life Timeline patch applied successfully.")
print()
print("Changed:")
print("  index.html")
print("  js/main.js")
print("  css/style.css")
print("  js/life-timeline-data.js")
print()
print("Backup:")
print(f"  {backup.name}")
print()
print("NEXT:")
print("  1. Edit js/life-timeline-data.js and enter the real dates/captions.")
print("  2. Open index.html locally and test thumbnail clicks, arrows and metadata.")
print("  3. Only after testing, push with your normal Git workflow.")
