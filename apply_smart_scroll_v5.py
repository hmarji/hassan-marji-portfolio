from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"

if not INDEX.exists():
    raise SystemExit("ERROR: index.html not found. Put this patch in the portfolio root folder.")

html = INDEX.read_text(encoding="utf-8")

# Remove previous smart/strong scroll policy blocks.
html = re.sub(r'\s*<script>\s*// HM_SCROLL_POLICY_V4_SMART.*?</script>\s*', '\n', html, flags=re.S)
html = re.sub(r'\s*<script>\s*// HM_SCROLL_POLICY_V3_STRONG.*?</script>\s*', '\n', html, flags=re.S)
html = re.sub(r'\s*<script>\s*// HM_SCROLL_POLICY_V2.*?</script>\s*', '\n', html, flags=re.S)

block = '''  <script>
    // HM_SCROLL_POLICY_V5_SMART_FIXED
    // Fresh visit -> hero.
    // Refresh -> stay exactly where you are.
    // Back/Forward -> browser handles normally.
    (function () {
      var nav = performance.getEntriesByType &&
                performance.getEntriesByType('navigation')[0];
      var type = nav && nav.type ? nav.type : 'navigate';
      var key = 'hm-scroll:' + location.pathname;

      function currentY() {
        return window.scrollY || document.documentElement.scrollTop || 0;
      }

      function saveY(y) {
        try {
          sessionStorage.setItem(key, String(Math.max(0, Number(y) || 0)));
        } catch (_) {}
      }

      function readY() {
        try {
          return Number(sessionStorage.getItem(key) || 0);
        } catch (_) {
          return 0;
        }
      }

      function restore(y) {
        y = Math.max(0, Number(y) || 0);
        window.scrollTo(0, y);
        requestAnimationFrame(function () {
          window.scrollTo(0, y);
          requestAnimationFrame(function () {
            window.scrollTo(0, y);
          });
        });
      }

      if (type === 'reload') {
        if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

        var saved = readY();

        document.addEventListener('DOMContentLoaded', function () {
          restore(saved);
        }, { once: true });

        window.addEventListener('load', function () {
          restore(saved);
        }, { once: true });

        window.addEventListener('pageshow', function () {
          restore(saved);
          setTimeout(function () { restore(saved); }, 80);
        }, { once: true });

      } else if (type === 'back_forward') {
        if ('scrollRestoration' in history) history.scrollRestoration = 'auto';

      } else {
        if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

        if (!location.hash) {
          // CRITICAL FIX: a brand-new visit must also reset the remembered
          // refresh position, otherwise an old timeline position can survive.
          saveY(0);

          window.scrollTo(0, 0);
          document.addEventListener('DOMContentLoaded', function () {
            window.scrollTo(0, 0);
          }, { once: true });
          window.addEventListener('load', function () {
            window.scrollTo(0, 0);
          }, { once: true });
        }
      }

      // Remember the user's real position after the page is established.
      var ticking = false;
      window.addEventListener('scroll', function () {
        if (!ticking) {
          requestAnimationFrame(function () {
            saveY(currentY());
            ticking = false;
          });
          ticking = true;
        }
      }, { passive: true });

      window.addEventListener('pagehide', function () {
        saveY(currentY());
      });

      window.addEventListener('beforeunload', function () {
        saveY(currentY());
      });
    })();
  </script>
'''

viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">'
if viewport in html:
    html = html.replace(viewport, viewport + "\n" + block, 1)
else:
    html = html.replace("<head>", "<head>\n" + block, 1)

INDEX.write_text(html, encoding="utf-8")

print("SUCCESS - Smart Scroll V5 applied.")
print("Fresh visit resets remembered position to 0.")
print("Refresh stays at the current position.")
print("Old stale timeline position can no longer come back after a fresh visit.")
