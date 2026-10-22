#!/usr/bin/env python3
"""
خادم الويب لنموذج الترجمة المتقدم Meta NLLB-200 (100% أوفلاين)
"""
import os
import sys
import json
import time
import socket
import threading
import webbrowser
import urllib.parse
from pathlib import Path
from http import HTTPStatus
from http.server import HTTPServer, ThreadingHTTPServer, SimpleHTTPRequestHandler

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from engine import NllbTranslationEngine

STATIC_DIR = CURRENT_DIR / "static"


class NllbRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(CURRENT_DIR), **kwargs)

    def _serve_file(self, file_path: Path, content_type: str):
        if not file_path.exists():
            self.send_error(404, "File not found")
            return
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def _send_json_response(self, data: dict, status_code: int = 200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(body)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path in ("/", "/index.html"):
            return self._serve_file(STATIC_DIR / "index.html", "text/html")

        if path in ("/static/style.css", "/style.css"):
            return self._serve_file(STATIC_DIR / "style.css", "text/css")

        if path in ("/static/app.js", "/app.js"):
            return self._serve_file(STATIC_DIR / "app.js", "application/javascript")

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if path == "/api/status":
            engine = NllbTranslationEngine.get_instance()
            return self._send_json_response({
                "status": "ready",
                "model": "Meta NLLB-200 distilled 600M (CTranslate2 int8)",
                "legacy_comparison_available": engine.argos_translator is not None,
                "offline": True,
            })

        return super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        try:
            if path == "/api/translate":
                data = self._read_json_body()
                text = data.get("text", "")
                engine = NllbTranslationEngine.get_instance()
                result = engine.translate_full_comparison(text)
                return self._send_json_response(result)

            self._send_json_response({"error": "Not Found"}, 404)
        except Exception as e:
            self._send_json_response({"error": str(e)}, 500)


def find_free_port(start_port: int = 8770, max_attempts: int = 20) -> int:
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start_port


def main():
    import argparse

    parser = argparse.ArgumentParser(description="NLLB-200 Offline Web Server")
    parser.add_argument("--port", type=int, default=8770, help="Port to listen on (default: 8770)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    print("==================================================================")
    print(" 🌟 Meta NLLB-200 AI Translator | المترجم العصبي فائق الجودة")
    print("==================================================================")
    print("[INIT] جاري تحميل نموذج Meta NLLB-200 المكمم int8...")
    
    t0 = time.time()
    engine = NllbTranslationEngine.get_instance()
    print(f"[INIT] تم تحميل النموذج في {time.time() - t0:.2f} ثانية!")

    port = find_free_port(args.port)
    server_address = (args.host, port)
    httpd = ThreadingHTTPServer(server_address, NllbRequestHandler)

    url = f"http://{args.host}:{port}"
    print(f"✨ الخادم يعمل الآن بدون إنترنت 100% على الرابط:")
    print(f"👉 \033[1;32m{url}\033[0m")
    print("------------------------------------------------------------------")

    if not args.no_browser:
        def open_browser():
            time.sleep(0.6)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        threading.Thread(target=open_browser, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] تم إيقاف الخادم.")
        sys.exit(0)


if __name__ == "__main__":
    main()
