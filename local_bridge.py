"""Loopback-only public/synthetic chat and brownie demo. Offline unless --live."""
import argparse
from dataclasses import asdict
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path
from threading import BoundedSemaphore
from urllib.parse import urlparse

from gera1.adapters.strict_json import loads_strict_json
from gera1.adapters.tavily import TavilySearch
from gera1.contracts.local_read import ReadContext
from gera1.orchestrator.brownie import synthesize_brownie
from gera1.orchestrator.chat import ChatInputError, converse, validate_chat
from gera1.orchestrator.delegation import delegation_route
from gera1.strands.research.percival import TRIGGER, research_halloween
from gera1.strands.marketing.montgomery import TRIGGER as MONTGOMERY_TRIGGER, create_halloween_draft
from gera1.workflows.demo_brownie import run_demo, encode
from gera1.workflows.synthetic_delegation import run_delegation

ROOT = Path(__file__).resolve().parent
UI = ROOT / "interface"
CONTEXT = ReadContext("synthetic-brownie-order", "synthetic-owner", "synthetic-bakery")


def evaluate_brownie(question, *, model=None):
    # Neither the question nor browser records determine file paths, identity or facts.
    result = run_demo(ROOT)
    answer = synthesize_brownie(result=result, context=CONTEXT, model=model)
    state = ("blocked" if answer.recommendation == "blocked" else
             "live" if answer.model_used else "fallback" if model is not None else "offline")
    return {"mode": "synthetic_" + state + "_demo", "question": question,
            "result": asdict(result) if state != "blocked" else None,
            "toby": {**asdict(answer), "status": state},
            "scenario": "Fixed synthetic 13-piece brownie request; typed quantities and dates are not interpreted."}


class BridgeServer(ThreadingHTTPServer):
    def __init__(self, address=("127.0.0.1", 8765), *, model=None, researcher=None):
        if address[0] != "127.0.0.1":
            raise ValueError("This demo must bind to loopback")
        self.model = model
        self.researcher = researcher if researcher is not None else TavilySearch()
        self.review_slot = BoundedSemaphore(1)
        super().__init__(address, Handler)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI), **kwargs)

    def setup(self):
        super().setup()
        self.connection.settimeout(30)

    def log_message(self, format, *args):
        # Do not log arbitrary request URLs, questions or provider exceptions.
        pass

    def _send(self, status, payload):
        raw = json.dumps(payload, default=encode).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _local_host(self):
        port = self.server.server_port
        return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

    def _delegate(self):
        # HTTP/1.0 close-delimited NDJSON: one bounded response, no polling or retries.
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        size = 0

        def emit(event):
            nonlocal size
            raw = (json.dumps(event, default=encode, ensure_ascii=True) + "\n").encode("utf-8")
            size += len(raw)
            if len(raw) > 16384 or size > 32768:
                raise ValueError("Delegation response limit")
            self.wfile.write(raw)
            self.wfile.flush()

        try:
            run_delegation(ROOT, emit)
        except Exception:
            # A stream already has headers. Closing without a final event means interrupted,
            # never a second HTTP response or a fabricated successful assessment.
            pass

    def _static(self, *, head=False):
        if not self._local_host():
            self._send(403, {"error": "Local host required"}); return
        path = urlparse(self.path).path
        relative = "index.html" if path == "/" else path.lstrip("/")
        allowed = relative in ("index.html", "script.js", "styles.css") or (
            relative.startswith("assets/") and len(Path(relative).parts) == 2
            and Path(relative).suffix in (".png", ".webp"))
        target = UI / relative
        if (not allowed or any(p.is_symlink() for p in (UI, target.parent, target))
                or not target.is_file() or not target.resolve().is_relative_to(UI.resolve())):
            self._send(404, {"error": "Not found"}); return
        if head:
            super().do_HEAD()
        else:
            super().do_GET()

    def do_GET(self):
        self._static()

    def do_HEAD(self):
        self._static(head=True)

    def do_POST(self):
        if (not self._local_host()
                or self.headers.get("Origin") != "http://" + self.headers.get("Host", "")
                or self.headers.get("Sec-Fetch-Site", "same-origin") != "same-origin"):
            self._send(403, {"error": "Same-origin local request required"}); return
        if self.path not in ("/api/brownie-demo", "/api/chat"):
            self._send(404, {"error": "Not found"}); return
        if self.headers.get_content_type() != "application/json":
            self._send(415, {"error": "JSON required"}); return
        try:
            if self.headers.get("Transfer-Encoding") or len(self.headers.get_all("Content-Length", [])) != 1:
                raise ValueError()
            length = int(self.headers["Content-Length"])
        except (ValueError, TypeError):
            self._send(400, {"error": "Invalid request length"}); return
        is_chat = self.path == "/api/chat"
        if not 0 < length <= (49152 if is_chat else 4096):
            self._send(413, {"error": "Request exceeds limit"}); return
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError()
            body = loads_strict_json(raw.decode("utf-8"))
            if is_chat:
                validate_chat(body)
            else:
                if not isinstance(body, dict) or set(body) != {"question"}:
                    raise ValueError()
                question = body["question"]
                if (not isinstance(question, str) or not 1 <= len(question.strip()) <= 1000
                        or "brownie" not in question.lower()):
                    raise ValueError()
        except ChatInputError as error:
            self._send(400, {"error": str(error), "error_code": error.code}); return
        except (ValueError, UnicodeError, TimeoutError, RecursionError):
            message = "Invalid chat JSON or text" if is_chat else "Supply only a brownie question of at most 1000 characters"
            self._send(400, {"error": message}); return
        if not self.server.review_slot.acquire(blocking=False):
            self._send(429, {"error": "A request is already running; try again when it finishes"}); return
        try:
            if is_chat:
                normalized = body["message"].strip().rstrip(".!?").casefold()
                if normalized == MONTGOMERY_TRIGGER.rstrip(".!?").casefold():
                    researcher = getattr(self.server, "researcher", None) or TavilySearch()
                    self._send(200, create_halloween_draft(search=researcher, model=self.server.model))
                elif normalized == TRIGGER.rstrip(".!?").casefold():
                    researcher = getattr(self.server, "researcher", None) or TavilySearch()
                    self._send(200, research_halloween(search=researcher))
                elif delegation_route(body["message"]) == "assess":
                    if "application/x-ndjson" not in self.headers.get("Accept", ""):
                        self._send(409, {"error": "Reload the interface to receive specialist activity; no checks ran"})
                    else:
                        self._delegate()
                else:
                    self._send(200, {"mode": "conversation", "chat": asdict(converse(body, model=self.server.model))})
            else:
                payload = evaluate_brownie(question, model=self.server.model)
                self._send(200 if payload["toby"]["status"] != "blocked" else 503, payload)
        except Exception:
            message = "Conversation unavailable; no action was taken" if is_chat else "Synthetic review unavailable; no order was accepted"
            self._send(503, {"error": message})
        finally:
            self.server.review_slot.release()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Enable Nebius replies for public/synthetic chat and brownie reviews using the server's NEBIUS_API_KEY")
    args = parser.parse_args()
    model = None
    if args.live:
        from gera1.adapters.nebius import NebiusTextModel
        model = NebiusTextModel()
    mode = "live replies enabled; connection not checked at startup" if args.live else "offline; no model calls"
    print(f"Open http://127.0.0.1:8765 — public/synthetic messages only; {mode}. Ctrl+C to stop.", flush=True)
    with BridgeServer(model=model) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
