from __future__ import annotations

import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


class FrontendHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self._is_api_request():
            self._proxy_request()
            return

        path = self.path.split("?", 1)[0]
        if path in ("", "/"):
            path = "/index.html"
        safe_path = (ROOT_DIR / path.lstrip("/")).resolve()
        if safe_path.exists() and safe_path.is_file() and str(safe_path).startswith(str(ROOT_DIR)):
            self._serve_file(safe_path)
            return
        self._serve_file(ROOT_DIR / "index.html")

    def do_POST(self) -> None:  # noqa: N802
        if self._is_api_request():
            self._proxy_request()
            return
        self.send_error(404)

    def do_PUT(self) -> None:  # noqa: N802
        if self._is_api_request():
            self._proxy_request()
            return
        self.send_error(404)

    def do_DELETE(self) -> None:  # noqa: N802
        if self._is_api_request():
            self._proxy_request()
            return
        self.send_error(404)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _is_api_request(self) -> bool:
        return self.path.startswith("/api")

    def _proxy_request(self) -> None:
        parsed = urlparse(self.path)
        target_path = parsed.path
        if target_path.startswith("/api"):
            target_path = target_path[4:] or "/"
        target_url = f"{BACKEND_URL}{target_path}"
        if parsed.query:
            target_url = f"{target_url}?{parsed.query}"

        body = None
        headers = {}
        if self.headers.get("Content-Length"):
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
        if self.headers.get("Content-Type"):
            headers["Content-Type"] = self.headers.get("Content-Type")

        request = urllib.request.Request(target_url, data=body, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                payload = response.read()
                self.send_response(response.status)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                for key, value in response.headers.items():
                    if key.lower() not in {"content-length", "transfer-encoding", "content-encoding"}:
                        self.send_header(key, value)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as error:
            payload = error.read()
            self.send_response(error.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def _serve_file(self, file_path: Path) -> None:
        content = file_path.read_bytes()
        content_type = "text/html"
        if file_path.suffix == ".css":
            content_type = "text/css"
        elif file_path.suffix == ".js":
            content_type = "application/javascript"
        elif file_path.suffix == ".json":
            content_type = "application/json"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8001"))
    server = ThreadingHTTPServer((host, port), FrontendHandler)
    print(f"Frontend server running on http://{host}:{port}")
    server.serve_forever()
