"""Process-local HTTP entity-body recording; no configuration or credential writes."""
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import datetime
import hashlib
import json
import os
import requests

_CAPTURE_DIR = None
_COUNTER = 0
_SECRET_FIELDS = {"api_key", "apikey", "key", "token", "access_token", "secret", "password", "email", "mailto"}


def configure_capture(raw_dir):
    global _CAPTURE_DIR, _COUNTER
    if raw_dir is None:
        _CAPTURE_DIR = None
        return
    path = Path(raw_dir)
    if path.is_symlink():
        raise ValueError("raw directory must not be a symlink")
    path.mkdir(mode=0o700, parents=False, exist_ok=False)
    _CAPTURE_DIR = path.resolve()
    _COUNTER = 0


def safe_url(url):
    parts = urlsplit(url)
    host = parts.hostname or ""
    if parts.port:
        host += ":" + str(parts.port)
    query = urlencode([(k, "[REDACTED]" if k.lower() in _SECRET_FIELDS else v)
                       for k, v in parse_qsl(parts.query, keep_blank_values=True)])
    return urlunsplit((parts.scheme, host, parts.path, query, ""))


def save_response(response, directory):
    global _COUNTER
    _COUNTER += 1
    body = response.content  # HTTP entity bytes after requests transport decompression.
    request = response.request
    url = request.url if request is not None else response.url
    secrets = [v for k, v in parse_qsl(urlsplit(url).query) if k.lower() in _SECRET_FIELDS and v]
    if request is not None:
        auth = request.headers.get("Authorization", "")
        if auth:
            secrets.extend([auth, auth.split()[-1]])
    leaked = any(len(s) >= 4 and s.encode() in body for s in secrets)
    stem = f"response-{_COUNTER:04d}"
    metadata = {"captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "method": request.method if request is not None else None,
                "url": safe_url(url), "http_status": response.status_code,
                "body_sha256": hashlib.sha256(body).hexdigest(), "body_bytes": len(body),
                "body_file": None if leaked else stem + ".bin",
                "body_saved": not leaked,
                "content_type": response.headers.get("Content-Type"),
                "capture_scope": "transport-decoded HTTP response entity; no request secrets or cookies",
                "notice": "response echoed a request secret; body intentionally omitted" if leaked else None}
    if not leaked:
        body_path = directory / (stem + ".bin")
        with body_path.open("xb") as handle:
            os.chmod(body_path, 0o600)
            handle.write(body)
    meta_path = directory / (stem + ".json")
    with meta_path.open("x", encoding="utf-8") as handle:
        os.chmod(meta_path, 0o600)
        json.dump(metadata, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    if leaked:
        raise requests.RequestException("response echoed a request credential/contact; hash and omission recorded, body not saved")
    return response


class RecordingSession(requests.Session):
    def send(self, request, **kwargs):
        if _CAPTURE_DIR is None:
            raise requests.RequestException("network use requires --raw-dir with a new local directory")
        response = super().send(request, **kwargs)
        return save_response(response, _CAPTURE_DIR)


def recording_session():
    return RecordingSession()
