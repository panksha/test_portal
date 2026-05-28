# -*- coding: utf-8 -*-
"""
Unified Launcher — run.py
Starts the Flask target app on port 5000 and the Dashboard API server
on port 8000 concurrently. Both servers are managed as background threads.
"""

import os
import sys
import json
import time
import signal
import logging
import threading
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "showcase_dashboard")
QA_FRAMEWORK_DIR = os.path.join(BASE_DIR, "qa_framework")
REPORTS_DIR = os.path.join(QA_FRAMEWORK_DIR, "reports")
HEALING_LOG = os.path.join(REPORTS_DIR, "healing_log.json")
INTERVIEW_PREP = os.path.join(DASHBOARD_DIR, "data", "interview_prep.json")

# ── Flask App Thread ────────────────────────────────────────────────────────

def start_flask_app():
    """Start the Flask target application."""
    flask_script = os.path.join(BASE_DIR, "target_app", "app.py")
    env = os.environ.copy()
    env["PORT"] = "5000"
    subprocess.Popen([sys.executable, flask_script], env=env)
    logger.info("[OK] Flask Target App started at http://localhost:5000")


# ── Dashboard API Server ─────────────────────────────────────────────────────

class DashboardAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silence default HTTP logs

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, filepath, content_type="text/html"):
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # ── Static files ──
        if path == "/" or path == "/index.html":
            self.send_file(os.path.join(DASHBOARD_DIR, "index.html"), "text/html")
        elif path.startswith("/assets/"):
            rel = path.lstrip("/")
            fpath = os.path.join(DASHBOARD_DIR, rel)
            ctype = "text/css" if path.endswith(".css") else "application/javascript"
            self.send_file(fpath, ctype)
        elif path.startswith("/data/"):
            rel = path.lstrip("/")
            fpath = os.path.join(DASHBOARD_DIR, rel)
            self.send_file(fpath, "application/json")

        # ── API endpoints ──
        elif path == "/api/get-prep-data":
            try:
                with open(INTERVIEW_PREP, "r") as f:
                    data = json.load(f)
                self.send_json(data)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        elif path == "/api/get-healing-logs":
            if os.path.exists(HEALING_LOG):
                with open(HEALING_LOG, "r") as f:
                    data = json.load(f)
            else:
                data = {"events": [], "total_heals": 0}
            self.send_json(data)

        elif path == "/api/locator-status":
            import urllib.request
            try:
                with urllib.request.urlopen("http://localhost:5000/api/locator-status", timeout=2) as r:
                    self.send_json(json.loads(r.read()))
            except Exception:
                self.send_json({"break_locators_active": False, "error": "Flask app not reachable"})

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path == "/api/run-tests":
            self._run_tests(payload)

        elif path == "/api/analyze-regression":
            self._analyze_regression(payload)

        elif path == "/api/toggle-locators":
            self._toggle_locators(payload)

        elif path == "/api/map-work-item":
            self._map_work_item(payload)

        else:
            self.send_json({"error": "Not found"}, 404)

    def _run_tests(self, payload):
        suite = payload.get("suite", "all")
        os.makedirs(os.path.join(REPORTS_DIR, "html"), exist_ok=True)
        os.makedirs(os.path.join(REPORTS_DIR, "screenshots"), exist_ok=True)

        if suite == "registration":
            test_path = os.path.join(QA_FRAMEWORK_DIR, "tests", "test_registration.py")
        elif suite == "forgot_password":
            test_path = os.path.join(QA_FRAMEWORK_DIR, "tests", "test_forgot_password.py")
        else:
            test_path = os.path.join(QA_FRAMEWORK_DIR, "tests")

        report_path = os.path.join(REPORTS_DIR, "html", "report.html")
        cmd = [
            sys.executable, "-m", "pytest", test_path,
            f"--html={report_path}",
            "--self-contained-html",
            "-v", "--tb=short", "--no-header"
        ]

        logger.info(f"[RUN] Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, cwd=BASE_DIR)
            self.send_json({
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report_path": report_path,
                "message": "Tests completed successfully" if result.returncode == 0 else "Some tests failed"
            })
        except subprocess.TimeoutExpired:
            self.send_json({"success": False, "error": "Test execution timed out after 180 seconds"}, 500)
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)

    def _analyze_regression(self, payload):
        changed = payload.get("changed_files", ["RegistrationController"])
        if isinstance(changed, str):
            changed = [c.strip() for c in changed.split(",")]
        sys.path.insert(0, BASE_DIR)
        try:
            from qa_framework.regression_analyzer import analyze
            result = analyze(changed)
            self.send_json(result)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def _toggle_locators(self, payload):
        import urllib.request
        active = payload.get("active")
        try:
            req_body = json.dumps({"active": active}).encode()
            req = urllib.request.Request(
                "http://localhost:5000/api/break-locators",
                data=req_body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3) as r:
                self.send_json(json.loads(r.read()))
        except Exception as e:
            self.send_json({"success": False, "error": f"Could not reach Flask app: {str(e)}"}, 500)

    def _map_work_item(self, payload):
        work_item_id = payload.get("id", "WI-001")
        sys.path.insert(0, BASE_DIR)
        try:
            backlog_path = os.path.join(BASE_DIR, "work_items", "backlog.json")
            with open(backlog_path, "r") as f:
                data = json.load(f)
            item = next((wi for wi in data["work_items"] if wi["id"] == work_item_id), None)
            if item:
                self.send_json({"success": True, "work_item": item})
            else:
                self.send_json({"success": False, "error": f"Work item {work_item_id} not found"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)


def start_dashboard_server():
    server = HTTPServer(("0.0.0.0", 8000), DashboardAPIHandler)
    logger.info("[DASH] Dashboard running at http://localhost:8000")
    server.serve_forever()


# ── Entry Point ──────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  [AI] AI-Driven QA Automation -- Demo Framework")
    print("="*60)

    # Start Flask target app
    start_flask_app()
    time.sleep(2)

    # Start Dashboard in a background thread
    dashboard_thread = threading.Thread(target=start_dashboard_server, daemon=True)
    dashboard_thread.start()

    print("\n  [OK] All services started successfully!")
    print("\n  URLs:")
    print("     [WEB]  Target Portal    : http://localhost:5000")
    print("     [FORM] Registration     : http://localhost:5000/register")
    print("     [KEY]  Forgot Password  : http://localhost:5000/forgot-password")
    print("     [DASH] QA Dashboard     : http://localhost:8000")
    print("\n  Quick Commands:")
    print("     Run all tests  : pytest qa_framework/tests/ -v")
    print("     Run reg tests  : pytest qa_framework/tests/test_registration.py -v")
    print("     Run fp tests   : pytest qa_framework/tests/test_forgot_password.py -v")
    print("\n  Press Ctrl+C to stop.\n" + "="*60 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
