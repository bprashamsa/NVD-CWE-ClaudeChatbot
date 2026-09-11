"""Local browser interface for the NVD + CWE chatbot."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from main import answer_question
from tools.formatting import format_answer


class ChatHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(size))
            question = payload.get("question", "").strip()
            if not question:
                raise ValueError("Please enter a question.")
            response = {"answer": format_answer(answer_question(question))}
        except (ValueError, json.JSONDecodeError) as exc:
            response = {"error": str(exc)}
        except Exception as exc:  # noqa: BLE001 - return external API errors to the UI
            response = {"error": f"Lookup failed: {exc}"}
        self._send(json.dumps(response), "application/json")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send(self, content, content_type):
        encoded = content.encode()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self._send_cors_headers()
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ChatHandler)
    print("Chat API available at http://127.0.0.1:8000/api/chat")
    server.serve_forever()