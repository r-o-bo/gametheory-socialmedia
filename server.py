"""Tiny web server (standard library only): python server.py [port]"""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from game_theory import ACTIONS, STRATEGIES, Game, simulate

INDEX = Path(__file__).parent / "static" / "index.html"


def parse_payoffs(data: dict) -> Game:
    """Accepts {"Invest|Invest": [a, b], ...}."""
    payoffs = {}
    for key, pair in data.items():
        a, b = key.split("|")
        payoffs[(a, b)] = tuple(pair)
    return Game(payoffs)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        raw = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, INDEX.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/meta":
            self._send(200, {"actions": ACTIONS, "strategies": list(STRATEGIES)})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            game = parse_payoffs(data["payoffs"])
            if self.path == "/api/analyze":
                self._send(200, game.analyze())
            elif self.path == "/api/simulate":
                self._send(200, simulate(
                    game, data["a"], data["b"],
                    int(data.get("rounds", 20)), float(data.get("discount", 1.0)),
                ))
            else:
                self._send(404, {"error": "not found"})
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
            self._send(400, {"error": str(e)})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Serving on http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
