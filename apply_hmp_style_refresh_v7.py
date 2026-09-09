from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"

if not INDEX.exists():
    raise SystemExit("ERROR: index.html not found. Put this patch in the portfolio root folder.")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / f"index.backup_before_hmp_refresh_{stamp}.html"
shutil.copy2(INDEX, backup)

html = INDEX.read_text(encoding="utf-8")

for marker in [
    "HM_SCROLL_POLICY_V7_HMP_STYLE",
    "HM_SCROLL_POLICY_V6_SILENT",
    "HM_SCROLL_POLICY_V5_SMART_FIXED",
    "HM_SCROLL_POLICY_V4_SMART",
    "HM_SCROLL_POLICY_V3_STRONG",
    "HM_SCROLL_POLICY_V2"
]:
    html = re.sub(
        rf'\s*<script>\s*// {re.escape(marker)}.*?</script>\s*',
        '\n',
        html,
        flags=re.S
    )

html = re.sub(
    r'\s*<style[^>]*id=["\']hm-refresh-restore-style["\'][^>]*>.*?</style>\s*',
    '\n',
    html,
    flags=re.S | re.I
)

nav = re.search(r'(<nav class="site-nav"[^>]*>)(.*?)(</nav>)', html, re.S)
if nav:
    body = nav.group(2)
    if not re.search(r'href=["\']#top["\'][^>]*>\s*Home\s*</a>', body, re.I):
        body = '\n      <a href="#top">Home</a>' + body
        html = html[:nav.start(2)] + body + html[nav.end(2):]

footer = re.search(r'<footer\b[^>]*>.*?</footer>', html, re.S | re.I)
if footer:
    block = footer.group(0)
    if not re.search(r'href=["\']#top["\'][^>]*>\s*Home\s*</a>', block, re.I):
        about_link = re.search(r'<a[^>]+href=["\']#about["\'][^>]*>', block, re.I)
        if about_link:
            block = (
                block[:about_link.start()]
                + '<a href="#top">Home</a>\n        '
                + block[about_link.start():]
            )
            html = html[:footer.start()] + block + html[footer.end():]

style = '  <style id="hm-refresh-restore-style">\n    html.hm-refresh-restoring {\n      visibility: hidden !important;\n      scroll-behavior: auto !important;\n    }\n    html.hm-refresh-restoring * {\n      scroll-behavior: auto !important;\n    }\n  </style>\n'
script_block = "  <script>\n    // HM_SCROLL_POLICY_V7_HMP_STYLE\n    (function () {\n      var nav = performance.getEntriesByType &&\n                performance.getEntriesByType('navigation')[0];\n      var type = nav && nav.type ? nav.type : 'navigate';\n      var key = 'hm-scroll:' + location.pathname;\n      var root = document.documentElement;\n\n      function yNow() {\n        return window.scrollY || root.scrollTop || 0;\n      }\n\n      function save(y) {\n        try {\n          sessionStorage.setItem(key, String(Math.max(0, Number(y) || 0)));\n        } catch (_) {}\n      }\n\n      function read() {\n        try {\n          return Math.max(0, Number(sessionStorage.getItem(key) || 0));\n        } catch (_) {\n          return 0;\n        }\n      }\n\n      function jump(y) {\n        y = Math.max(0, Number(y) || 0);\n        window.scrollTo({ top: y, left: 0, behavior: 'auto' });\n        root.scrollTop = y;\n        if (document.body) document.body.scrollTop = y;\n      }\n\n      function wait(ms) {\n        return new Promise(function (resolve) {\n          setTimeout(resolve, ms);\n        });\n      }\n\n      function nextFrame() {\n        return new Promise(function (resolve) {\n          requestAnimationFrame(function () {\n            requestAnimationFrame(resolve);\n          });\n        });\n      }\n\n      function domReady() {\n        if (document.readyState !== 'loading') return Promise.resolve();\n        return new Promise(function (resolve) {\n          document.addEventListener('DOMContentLoaded', resolve, { once: true });\n        });\n      }\n\n      function windowLoaded() {\n        if (document.readyState === 'complete') return Promise.resolve();\n        return new Promise(function (resolve) {\n          window.addEventListener('load', resolve, { once: true });\n        });\n      }\n\n      if (type === 'reload') {\n        if ('scrollRestoration' in history) history.scrollRestoration = 'manual';\n\n        var target = read();\n        var revealed = false;\n        root.classList.add('hm-refresh-restoring');\n\n        function reveal() {\n          if (revealed) return;\n          revealed = true;\n          jump(target);\n          root.classList.remove('hm-refresh-restoring');\n        }\n\n        var fallback = setTimeout(reveal, 1800);\n\n        (async function () {\n          await domReady();\n          jump(target);\n\n          if (document.fonts && document.fonts.ready) {\n            await Promise.race([\n              document.fonts.ready.catch(function () {}),\n              wait(300)\n            ]);\n          }\n\n          await Promise.race([windowLoaded(), wait(650)]);\n          jump(target);\n\n          var lastHeight = -1;\n          var stableCount = 0;\n\n          for (var i = 0; i < 8; i++) {\n            await wait(45);\n            jump(target);\n\n            var h = Math.max(\n              document.documentElement.scrollHeight,\n              document.body ? document.body.scrollHeight : 0\n            );\n\n            if (Math.abs(h - lastHeight) <= 1) {\n              stableCount++;\n            } else {\n              stableCount = 0;\n              lastHeight = h;\n            }\n\n            if (stableCount >= 2) break;\n          }\n\n          await nextFrame();\n          jump(target);\n          clearTimeout(fallback);\n          reveal();\n        })();\n\n      } else if (type === 'back_forward') {\n        if ('scrollRestoration' in history) history.scrollRestoration = 'auto';\n\n      } else {\n        if ('scrollRestoration' in history) history.scrollRestoration = 'manual';\n\n        if (!location.hash) {\n          save(0);\n          jump(0);\n\n          document.addEventListener('DOMContentLoaded', function () {\n            jump(0);\n          }, { once: true });\n\n          window.addEventListener('load', function () {\n            jump(0);\n          }, { once: true });\n\n          window.addEventListener('pageshow', function () {\n            jump(0);\n          }, { once: true });\n        }\n      }\n\n      var ticking = false;\n      window.addEventListener('scroll', function () {\n        if (!ticking) {\n          ticking = true;\n          requestAnimationFrame(function () {\n            save(yNow());\n            ticking = false;\n          });\n        }\n      }, { passive: true });\n    })();\n  </script>\n"
insert = style + script_block

viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">'
if viewport in html:
    html = html.replace(viewport, viewport + "\n" + insert, 1)
elif "<head>" in html:
    html = html.replace("<head>", "<head>\n" + insert, 1)
else:
    shutil.copy2(backup, INDEX)
    raise SystemExit("ERROR: Could not find <head> or viewport meta tag.")

INDEX.write_text(html, encoding="utf-8")

final = INDEX.read_text(encoding="utf-8")
checks = {
    "V7 marker": "HM_SCROLL_POLICY_V7_HMP_STYLE" in final,
    "restore style": 'id="hm-refresh-restore-style"' in final,
    "top Home": bool(re.search(r'<nav class="site-nav".*?href="#top"[^>]*>\s*Home\s*</a>', final, re.S | re.I)),
    "no V6 marker": "HM_SCROLL_POLICY_V6_SILENT" not in final,
    "no V5 marker": "HM_SCROLL_POLICY_V5_SMART_FIXED" not in final
}
failed = [name for name, ok in checks.items() if not ok]

if failed:
    shutil.copy2(backup, INDEX)
    raise SystemExit("ERROR: Validation failed; original index restored. Failed: " + ", ".join(failed))

print("SUCCESS - HMP-style refresh behavior applied.")
print("Backup created:", backup.name)
print("Fresh/direct opening -> hero/top.")
print("Refresh -> same position, hidden until layout settles, then revealed.")
print("No animated scroll-back during refresh.")
print("Normal menu anchor navigation remains unchanged.")
print("Home remains/adds in top navigation and footer.")
