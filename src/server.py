import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.runner import run_lead_scoring_agent


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            path = "/index.html"
        file_path = (PUBLIC_DIR / path.lstrip("/")).resolve()

        if not str(file_path).startswith(str(PUBLIC_DIR.resolve())) or not file_path.exists():
            self._send_json({"error": "Not found"}, status=404)
            return

        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(file_path.read_bytes())

    def do_POST(self):
        if urlparse(self.path).path != "/api/analyze-lead":
            self._send_json({"error": "Not found"}, status=404)
            return

        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.loads(body.decode("utf-8"))
            result = run_lead_scoring_agent(payload)
            self._send_json(result)
        except ValueError as error:
            self._send_json({"error": str(error)}, status=400)
        except Exception as error:
            self._send_json({"error": f"分析失败：{error}"}, status=500)

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), DemoHandler)
    print("AI Growth Copilot demo running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
