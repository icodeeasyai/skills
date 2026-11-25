#!/usr/bin/env python3
"""Quote, create, recover, and download iCodeEasy 3D generation tasks."""

from __future__ import annotations

import argparse
import base64
import http.client
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


API_BASES = {"https://api.icodeeasy.ai", "https://jp.icodeeasy.ai", "https://sg.icodeeasy.ai",
             "https://api.icodeeasy.cc", "https://jp.icodeeasy.cc", "https://sg.icodeeasy.cc"}
INPUTS = ("prompt", "image_url", "image_base64", "image_views")
TERMINAL = {"completed", "failed", "submission_unknown"}


class OperationError(Exception):
    def __init__(self, message, *, status=None, detail=None):
        super().__init__(message)
        self.status = status
        self.detail = detail


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def positive_float(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return number


def emit(value, *, stream=None):
    stream = stream or sys.stdout
    print(json.dumps(value, ensure_ascii=False), file=stream, flush=True)


def base_url(args):
    value = args.base_url.rstrip("/")
    parsed = urllib.parse.urlsplit(value)
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path:
        raise ValueError("base URL must contain only a scheme and host")
    local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (local and parsed.scheme == "http" and args.allow_insecure_localhost):
        raise ValueError("use HTTPS, or explicitly allow HTTP localhost")
    if value not in API_BASES and not args.trust_custom_base_url:
        raise ValueError("custom API hosts require --trust-custom-base-url")
    if not parsed.hostname:
        raise ValueError("base URL requires a host")
    return value


def api_key():
    for name in ("ICODEEASY_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        if os.environ.get(name, "").strip():
            return os.environ[name].strip()
    raise ValueError("set ICODEEASY_API_KEY, OPENAI_API_KEY, or ANTHROPIC_AUTH_TOKEN")


def redact_secret(value, secret):
    if isinstance(value, str):
        return value.replace(secret, "<redacted>")
    if isinstance(value, list):
        return [redact_secret(item, secret) for item in value]
    if isinstance(value, dict):
        return {name: redact_secret(item, secret) for name, item in value.items()}
    return value


def request_json(url, key, timeout, *, payload=None, idempotency_key=None):
    headers = {"Authorization": "Bearer " + key, "Accept": "application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
            result = json.load(response)
        if not isinstance(result, dict):
            raise OperationError("API response must be a JSON object")
        return result
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read())
        except (ValueError, OSError, http.client.HTTPException):
            detail = None
        raise OperationError(f"API request returned HTTP {exc.code}", status=exc.code, detail=redact_secret(detail, key)) from exc
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException) as exc:
        raise OperationError("API connection failed or timed out") from exc
    except ValueError as exc:
        raise OperationError("API response contains invalid JSON") from exc


def load_request(args):
    if args.request == "-":
        payload = json.load(sys.stdin)
    else:
        with open(args.request, encoding="utf-8") as source:
            payload = json.load(source)
    if not isinstance(payload, dict) or not isinstance(payload.get("model"), str) or not payload["model"].strip():
        raise ValueError("request must be a JSON object containing model")
    if args.image_file:
        if any(payload.get(field) for field in INPUTS):
            raise ValueError("--image-file requires a request without another input")
        image = Path(args.image_file)
        if image.stat().st_size > 60 * 1024 * 1024:
            raise ValueError("Base64 image input must be at most 60 MiB")
        content = image.read_bytes()
        if not (content.startswith(b"\x89PNG\r\n\x1a\n") or content.startswith(b"\xff\xd8\xff")):
            raise ValueError("--image-file requires a PNG or JPEG")
        payload["image_base64"] = base64.b64encode(content).decode("ascii")
    selected = [name for name in INPUTS if payload.get(name)]
    if len(selected) != 1:
        raise ValueError("provide exactly one of prompt, image_url, image_base64, or image_views")
    return payload, "text" if selected[0] == "prompt" else "multiview" if selected[0] == "image_views" else "image"


def task_path(task_id):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,160}", task_id):
        raise ValueError("invalid task ID")
    return "/v1/3d/tasks/" + task_id


def validate_asset_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise OperationError("completed task has no valid HTTPS asset URL")
    if parsed.hostname == "localhost" or parsed.hostname.endswith(".localhost"):
        raise OperationError("asset URL must use a public host")
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        return
    if not address.is_global:
        raise OperationError("asset URL must use a public host")


class AssetRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_asset_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def poll(args, root, key, task_id, *, wait):
    deadline = time.monotonic() + args.max_wait
    while True:
        task = request_json(root + task_path(task_id), key, args.timeout)
        status = task.get("status")
        if status not in TERMINAL | {"queued", "processing"}:
            raise OperationError("unknown task status", detail=task)
        if status in TERMINAL or not wait:
            return task
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise OperationError("polling timed out; recover this task with poll", detail=task)
        time.sleep(min(args.interval, remaining))


def download(task, output, timeout, *, overwrite):
    if task.get("status") != "completed":
        raise OperationError("task must be completed before downloading", detail=task)
    url = task.get("asset_url", "")
    validate_asset_url(url)
    destination = Path(output).expanduser().absolute()
    if destination.exists() and not overwrite:
        raise ValueError("output exists; choose another path or pass --overwrite")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix="." + destination.name + ".", suffix=".part", delete=False) as target:
            temporary = Path(target.name)
            # Signed storage links authenticate themselves. API credentials stay on the API host.
            with urllib.request.build_opener(AssetRedirect).open(url, timeout=timeout) as response:
                content_length = response.headers.get("Content-Length")
                shutil.copyfileobj(response, target)
        if content_length is not None:
            try:
                expected_bytes = int(content_length)
            except ValueError as exc:
                raise OperationError("download returned invalid Content-Length") from exc
            if expected_bytes != temporary.stat().st_size:
                raise OperationError("download was truncated; retry download for the same task")
        if temporary.stat().st_size == 0:
            raise OperationError("download returned an empty file")
        if overwrite:
            os.replace(temporary, destination)
        else:
            os.link(temporary, destination)
        return str(destination)
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException) as exc:
        raise OperationError("download failed; retry download for the same task") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--base-url", default="https://api.icodeeasy.ai")
    result.add_argument("--trust-custom-base-url", action="store_true")
    result.add_argument("--allow-insecure-localhost", action="store_true")
    result.add_argument("--timeout", type=positive_float, default=60)
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("models", help="discover current models, modes, and prices")
    for name in ("quote", "create", "run"):
        command = commands.add_parser(name)
        command.add_argument("--request", required=True, help="generation JSON file, or - for stdin")
        command.add_argument("--image-file", help="local PNG/JPEG single-image reference")
        if name != "quote":
            command.add_argument("--confirm-paid", action="store_true")
            command.add_argument("--dry-run", action="store_true")
            command.add_argument("--idempotency-key")
    polling = commands.add_parser("poll")
    polling.add_argument("task_id")
    polling.add_argument("--wait", action="store_true")
    for command in (commands.choices["run"], polling):
        command.add_argument("--interval", type=positive_float, default=5)
        command.add_argument("--max-wait", type=positive_float, default=900)
    downloading = commands.add_parser("download")
    downloading.add_argument("task_id")
    downloading.add_argument("--output", required=True)
    commands.choices["run"].add_argument("--output")
    for command in (commands.choices["run"], downloading):
        command.add_argument("--overwrite", action="store_true")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    task_id = getattr(args, "task_id", None)
    idempotency_key = None
    submission_attempted = False
    task = None
    stage = args.command
    try:
        root = base_url(args)
        if args.command in {"run", "download"} and args.output:
            if Path(args.output).expanduser().exists() and not args.overwrite:
                raise ValueError("output exists; choose another path or pass --overwrite")
        if args.command in {"quote", "create", "run"}:
            payload, mode = load_request(args)
            if args.command == "quote":
                quote = {"model": payload["model"], "mode": mode, "texture": payload.get("texture", False)}
                if "options" in payload:
                    quote["options"] = payload["options"]
                emit(request_json(root + "/v1/3d/quote", api_key(), args.timeout, payload=quote))
                return 0
            idempotency_key = args.idempotency_key or "idem_" + uuid.uuid4().hex
            if len(idempotency_key) > 128 or not idempotency_key.strip() or any(ord(char) < 32 or ord(char) > 126 for char in idempotency_key):
                raise ValueError("idempotency key must contain 1–128 printable ASCII characters")
            if args.dry_run:
                preview = dict(payload)
                if "image_base64" in preview:
                    preview["image_base64"] = "<base64 image>"
                emit({"dry_run": True, "method": "POST", "url": root + "/v1/3d/generations", "idempotency_key": idempotency_key, "payload": preview})
                return 0
            if not args.confirm_paid:
                raise ValueError("creating a paid task requires --confirm-paid; use --dry-run to inspect")
            key = api_key()
            # Preserve the key before a submission can become uncertain.
            emit({"stage": "create", "idempotency_key": idempotency_key}, stream=sys.stderr)
            stage = "create"
            submission_attempted = True
            task = request_json(root + "/v1/3d/generations", key, args.timeout, payload=payload, idempotency_key=idempotency_key)
            task_id = task.get("id")
            if not isinstance(task_id, str) or not task_id:
                raise OperationError("generation response is missing its task ID", detail=task)
            if task.get("status") not in TERMINAL | {"queued", "processing"}:
                raise OperationError("unknown task status", detail=task)
            if args.command == "create":
                emit({**task, "idempotency_key": idempotency_key})
                return 1 if task.get("status") in {"failed", "submission_unknown"} else 0
            emit({"id": task_id, "status": task.get("status"), "idempotency_key": idempotency_key}, stream=sys.stderr)
            stage = "poll"
            if task.get("status") not in TERMINAL:
                task = poll(args, root, key, task_id, wait=True)
        elif args.command == "models":
            emit(request_json(root + "/v1/3d/models", api_key(), args.timeout))
            return 0
        else:
            key = api_key()
            if args.command == "poll":
                task = poll(args, root, key, task_id, wait=args.wait)
            else:
                task = request_json(root + task_path(task_id), key, args.timeout)
        result = dict(task)
        if idempotency_key:
            result["idempotency_key"] = idempotency_key
        if args.command == "download" or (args.command == "run" and args.output and task.get("status") == "completed"):
            stage = "download"
            result["output"] = download(task, args.output, args.timeout, overwrite=args.overwrite)
        emit(result)
        return 1 if task.get("status") in {"failed", "submission_unknown"} else 0
    except (OperationError, ValueError, OSError) as exc:
        error = {"message": str(exc), "stage": stage}
        if isinstance(exc, OperationError):
            error.update({"http_status": exc.status, "detail": exc.detail})
        result = {"error": error}
        if task_id:
            result["task_id"] = task_id
            result["recovery_action"] = "retry download for this task" if stage == "download" else "poll this task; do not create another"
        if idempotency_key:
            result["idempotency_key"] = idempotency_key
            status = exc.status if isinstance(exc, OperationError) else None
            if not task_id and submission_attempted and status == 409:
                result["recovery_action"] = "use the original request for this idempotency key or contact support"
            elif not task_id and submission_attempted and (status is None or status >= 500):
                result["recovery_action"] = "retry identical input with this idempotency key"
        if task:
            result["task"] = task
        emit(result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
