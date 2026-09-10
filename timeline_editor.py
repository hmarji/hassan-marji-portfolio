from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "js" / "life-timeline-data.js"
HOST = "127.0.0.1"
PORT = 8765

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/timeline":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, list):
                raise ValueError("Timeline payload must be a list.")
            cleaned = []
            for item in payload:
                if not isinstance(item, dict):
                    continue
                file = str(item.get("file", "")).strip()
                date = str(item.get("date", "")).strip()
                caption = str(item.get("caption", "")).strip()
                if not file:
                    continue
                if "/" in file or "\\" in file:
                    raise ValueError("Invalid timeline file name.")
                cleaned.append({"file": file, "date": date, "caption": caption})
            js = (
                "/* HM Portfolio — Life Timeline metadata\n"
                "   Written automatically by EDIT_TIMELINE.bat.\n"
                "   Date format: YYYY, YYYY-MM, or YYYY-MM-DD.\n"
                "*/\nwindow.HM_LIFE_TIMELINE = "
                + json.dumps(cleaned, ensure_ascii=False, indent=2)
                + ";\n"
            )
            DATA.parent.mkdir(parents=True, exist_ok=True)
            DATA.write_text(js, encoding="utf-8")
            body = json.dumps({"ok": True, "count": len(cleaned)}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            body = str(exc).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

if __name__ == "__main__":
    os.chdir(ROOT)
    url = f"http://{HOST}:{PORT}/?timeline-edit=1#life-timeline"
    print("HM Portfolio Timeline Editor")
    print("Use the settings control on any thumbnail. Saving updates js/life-timeline-data.js.")
    print(f"Editor URL: {url}")
    print("Press Ctrl+C here when finished.")
    threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
