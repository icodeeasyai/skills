"""Exercise the installed 3D task CLI without paid or external requests."""

from __future__ import annotations

import base64
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import http.client
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "model3d_task.py"
SPEC = importlib.util.spec_from_file_location("model3d_task", SCRIPT)
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6lAsAAAAASUVORK5CYII=")


@contextmanager
def fake_api():
    recorded = []
    states = ["processing", "completed"]

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            recorded.append((self.command, self.path, dict(self.headers), payload))
            if self.path.endswith("/quote"):
                body = {"price_rmb": 1.25}
                status = 200
            else:
                body = {"id": "3d_same_task", "status": "queued", "progress": 0}
                status = 202
            self.send_json(status, body)

        def do_GET(self):
            recorded.append((self.command, self.path, dict(self.headers), None))
            if self.path.endswith("/models"):
                self.send_json(200, {"data": [{"id": "hy-3d-3.1"}]})
            elif self.path.endswith("/download.glb"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"glTF-fake-asset")
            else:
                status = states.pop(0) if states else "completed"
                self.send_json(200, {"id": "3d_same_task", "status": status,
                                     "asset_url": "https://assets.example.test/download.glb", "cost_rmb": 1.25})

        def send_json(self, status, body):
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body).encode())

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    root = f"http://127.0.0.1:{server.server_port}"
    try:
        yield root, recorded, states
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def invoke(arguments, *, root=None):
    options = [] if root is None else ["--base-url", root, "--trust-custom-base-url", "--allow-insecure-localhost"]
    stdout, stderr = io.StringIO(), io.StringIO()
    with patch.dict(os.environ, {"ICODEEASY_API_KEY": "test-account-key"}, clear=True), redirect_stdout(stdout), redirect_stderr(stderr):
        code = cli.main(options + arguments)
    return code, json.loads(stdout.getvalue()), stderr.getvalue()


class Model3DTaskTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.request = self.root / "request.json"
        self.request.write_text(json.dumps({"model": "hy-3d-3.1", "prompt": "A teapot", "texture": False}), encoding="utf-8")

    def test_installed_script_dry_run_needs_no_auth_or_siblings(self):
        installed = self.root / "isolated" / "scripts" / SCRIPT.name
        installed.parent.mkdir(parents=True)
        shutil.copy2(SCRIPT, installed)
        run = subprocess.run([sys.executable, str(installed), "run", "--request", str(self.request), "--dry-run", "--idempotency-key", "known-key"], env={}, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["payload"]["model"], "hy-3d-3.1")
        self.assertEqual(result["idempotency_key"], "known-key")
        self.assertEqual(result["url"], "https://api.icodeeasy.ai/v1/3d/generations")

    def test_local_image_quote_preserves_options_and_omits_image_bytes(self):
        self.request.write_text(json.dumps({"model": "tripo-p2", "texture": True, "options": {"delight": True}}))
        image = self.root / "input.png"
        image.write_bytes(PNG)
        with fake_api() as (root, requests, _):
            code, result, _ = invoke(["quote", "--request", str(self.request), "--image-file", str(image)], root=root)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["price_rmb"], 1.25)
        self.assertEqual(requests[0][3], {"model": "tripo-p2", "mode": "image", "texture": True, "options": {"delight": True}})
        self.assertEqual(requests[0][2]["Authorization"], "Bearer test-account-key")

    def test_multiview_quote_infers_mode(self):
        self.request.write_text(json.dumps({"model": "hy-3d-3.1", "image_views": {"front": "https://example.com/front.png", "back": "https://example.com/back.png"}, "texture": False, "options": {"face_count": 50000}}))
        with fake_api() as (root, requests, _):
            code, _, _ = invoke(["quote", "--request", str(self.request)], root=root)
        self.assertEqual(code, 0)
        self.assertEqual(requests[0][3]["mode"], "multiview")
        self.assertEqual(requests[0][3]["options"], {"face_count": 50000})

    def test_local_image_dry_run_redacts_base64_and_validates_conflicts(self):
        self.request.write_text('{"model":"hy-3d-express","texture":false}')
        image = self.root / "input.png"
        image.write_bytes(PNG)
        with patch.object(cli, "request_json", side_effect=AssertionError("no network")):
            code, result, _ = invoke(["create", "--request", str(self.request), "--image-file", str(image), "--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(result["payload"]["image_base64"], "<base64 image>")
        self.request.write_text('{"model":"hy-3d-express","prompt":"conflict"}')
        code, result, _ = invoke(["create", "--request", str(self.request), "--image-file", str(image), "--dry-run"])
        self.assertEqual(code, 1)
        self.assertIn("another input", result["error"]["message"])

    def test_run_creates_once_polls_same_task_and_downloads_without_auth(self):
        output = self.root / "nested" / "model.glb"
        original_opener = urllib.request.build_opener

        with fake_api() as (root, requests, _):
            class DownloadOpener:
                def open(self, url, timeout):
                    self.assert_url = url
                    return urllib.request.urlopen(root + "/download.glb", timeout=timeout)

            def opener(*handlers):
                if handlers and handlers[0] is cli.AssetRedirect:
                    return DownloadOpener()
                return original_opener(*handlers)

            with patch.object(cli.urllib.request, "build_opener", side_effect=opener):
                code, result, progress = invoke(["run", "--request", str(self.request), "--confirm-paid", "--idempotency-key", "caller-key", "--interval", "0.001", "--output", str(output)], root=root)
        self.assertEqual(code, 0, result)
        self.assertEqual(output.read_bytes(), b"glTF-fake-asset")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["output"], str(output))
        self.assertIn("3d_same_task", progress)
        creates = [request for request in requests if request[0] == "POST"]
        self.assertEqual(len(creates), 1)
        self.assertEqual(creates[0][2]["Idempotency-Key"], "caller-key")
        downloads = [request for request in requests if request[1].endswith("download.glb")]
        self.assertEqual(len(downloads), 1)
        self.assertNotIn("Authorization", downloads[0][2])

    def test_paid_flag_and_existing_output_are_checked_before_network(self):
        output = self.root / "existing.glb"
        output.write_bytes(b"old")
        with patch.object(cli, "request_json", side_effect=AssertionError("no network")):
            code, _, _ = invoke(["create", "--request", str(self.request)])
            self.assertEqual(code, 1)
            code, _, _ = invoke(["run", "--request", str(self.request), "--confirm-paid", "--output", str(output)])
        self.assertEqual(code, 1)
        self.assertEqual(output.read_bytes(), b"old")

    def test_local_or_synchronous_rejections_do_not_claim_uncertain_submission(self):
        code, result, _ = invoke(["create", "--request", str(self.request)])
        self.assertEqual(code, 1)
        self.assertNotIn("recovery_action", result)
        for status in (400, 401, 402, 409):
            with self.subTest(status=status), patch.object(cli, "request_json", side_effect=cli.OperationError("rejected", status=status)):
                code, result, _ = invoke(["create", "--request", str(self.request), "--confirm-paid"])
            self.assertEqual(code, 1)
            if status == 409:
                self.assertIn("original request", result["recovery_action"])
            else:
                self.assertNotIn("recovery_action", result)

    def test_uncertain_submission_keeps_key_and_never_retries(self):
        with patch.object(cli, "request_json", side_effect=cli.OperationError("connection lost")) as request:
            code, result, _ = invoke(["create", "--request", str(self.request), "--confirm-paid", "--idempotency-key", "recover-key"])
        self.assertEqual(code, 1)
        self.assertEqual(request.call_count, 1)
        self.assertEqual(result["idempotency_key"], "recover-key")
        self.assertIn("identical input", result["recovery_action"])

    def test_download_failure_preserves_completed_task(self):
        with fake_api() as (root, requests, states), patch.object(cli, "download", side_effect=cli.OperationError("asset unavailable")):
            states[:] = ["completed"]
            code, result, _ = invoke(["run", "--request", str(self.request), "--confirm-paid", "--output", str(self.root / "asset.glb")], root=root)
        self.assertEqual(code, 1)
        self.assertEqual(result["task_id"], "3d_same_task")
        self.assertEqual(result["task"]["status"], "completed")
        self.assertEqual(result["error"]["stage"], "download")
        self.assertEqual(len([r for r in requests if r[0] == "POST"]), 1)

    def test_failed_and_submission_unknown_tasks_exit_without_recreating(self):
        for state in ("failed", "submission_unknown"):
            with self.subTest(state=state), fake_api() as (root, requests, states):
                states[:] = [state]
                code, result, _ = invoke(["poll", "3d_same_task", "--wait"], root=root)
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], state)
            self.assertEqual(len(requests), 1)

    def test_run_honors_terminal_create_or_idempotent_replay_response(self):
        for status in ("failed", "submission_unknown", "completed"):
            with self.subTest(status=status), patch.object(cli, "request_json", return_value={"id": "3d_same_task", "status": status}) as request:
                code, result, _ = invoke(["run", "--request", str(self.request), "--confirm-paid"])
            self.assertEqual(code, 0 if status == "completed" else 1)
            self.assertEqual(result["status"], status)
            self.assertEqual(request.call_count, 1)

    def test_truncated_download_keeps_destination_and_cleans_partial_file(self):
        response = io.BytesIO(b"ten-bytes!")
        response.headers = {"Content-Length": "100"}
        destination = self.root / "model.glb"
        destination.write_bytes(b"existing")
        task = {"id": "3d_same_task", "status": "completed", "asset_url": "https://cdn.example/model.glb"}
        with patch.object(cli.urllib.request, "build_opener") as opener:
            opener.return_value.open.return_value = response
            with self.assertRaisesRegex(cli.OperationError, "truncated"):
                cli.download(task, str(destination), 1, overwrite=True)
        self.assertEqual(destination.read_bytes(), b"existing")
        self.assertEqual(list(self.root.glob("*.part")), [])

    def test_incomplete_json_response_keeps_submission_key(self):
        with patch.object(cli.urllib.request, "build_opener") as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.read.side_effect = http.client.IncompleteRead(b'{"id":', 100)
            code, result, _ = invoke(["create", "--request", str(self.request), "--confirm-paid", "--idempotency-key", "recover-key"])
        self.assertEqual(code, 1)
        self.assertEqual(result["idempotency_key"], "recover-key")
        self.assertEqual(result["error"]["stage"], "create")
        self.assertIn("identical input", result["recovery_action"])

    def test_incomplete_error_response_keeps_http_status_and_submission_key(self):
        with patch.object(cli.urllib.request, "build_opener") as opener:
            body = unittest.mock.Mock()
            body.read.side_effect = http.client.IncompleteRead(b'{"error":', 100)
            opener.return_value.open.side_effect = urllib.error.HTTPError(
                "https://api.icodeeasy.ai", 502, "bad gateway", {}, body
            )
            code, result, _ = invoke([
                "create", "--request", str(self.request), "--confirm-paid",
                "--idempotency-key", "recover-key",
            ])
        self.assertEqual(code, 1)
        self.assertEqual(result["idempotency_key"], "recover-key")
        self.assertEqual(result["error"]["http_status"], 502)
        self.assertIn("identical input", result["recovery_action"])

    def test_server_error_redacts_echoed_api_key(self):
        failure = urllib.error.HTTPError("https://api.icodeeasy.ai", 401, "unauthorized", {}, io.BytesIO(b'{"error":{"message":"rejected test-account-key"}}'))
        with patch.object(cli.urllib.request, "build_opener") as opener:
            opener.return_value.open.side_effect = failure
            code, result, _ = invoke(["models"])
        self.assertEqual(code, 1)
        self.assertNotIn("test-account-key", json.dumps(result))
        self.assertIn("<redacted>", json.dumps(result))

    def test_poll_timeout_keeps_task_id_for_recovery(self):
        with fake_api() as (root, requests, states):
            states[:] = ["processing"] * 10
            code, result, _ = invoke(["poll", "3d_same_task", "--wait", "--interval", "0.001", "--max-wait", "0.002"], root=root)
        self.assertEqual(code, 1)
        self.assertEqual(result["task_id"], "3d_same_task")
        self.assertTrue(all(r[0] == "GET" for r in requests))

    def test_api_redirect_does_not_forward_credentials(self):
        class RedirectHandler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", "https://example.com/capture")
                self.end_headers()

        server = ThreadingHTTPServer(("127.0.0.1", 0), RedirectHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            code, result, _ = invoke(["models"], root=f"http://127.0.0.1:{server.server_port}")
            self.assertEqual(code, 1)
            self.assertEqual(result["error"]["http_status"], 302)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_credentials_precedence_and_untrusted_origins(self):
        with patch.dict(os.environ, {"ICODEEASY_API_KEY": "account", "OPENAI_API_KEY": "openai", "ANTHROPIC_AUTH_TOKEN": "anthropic"}, clear=True):
            self.assertEqual(cli.api_key(), "account")
            del os.environ["ICODEEASY_API_KEY"]
            self.assertEqual(cli.api_key(), "openai")
        with patch.object(cli, "request_json", side_effect=AssertionError("no network")):
            for url in ("https://untrusted.example", "http://localhost:8000", "https://api.icodeeasy.ai@evil.example", "https://api.icodeeasy.ai/extra"):
                code, _, _ = invoke(["--base-url", url, "models"])
                self.assertEqual(code, 1)

    def test_asset_url_rejects_downgrade_and_private_hosts(self):
        for url in ("http://cdn.example/model.glb", "https://127.0.0.1/model.glb", "https://localhost/model.glb", "https://10.0.0.1/model.glb"):
            with self.subTest(url=url), self.assertRaises(cli.OperationError):
                cli.validate_asset_url(url)
        cli.validate_asset_url("https://cdn.example/model.glb?signature=abc")


if __name__ == "__main__":
    unittest.main()
