"""Shared deterministic bundle rules. No network, OCR, Git, or vault operations."""
from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo

SCHEMA_VERSION = "1.0"
META_FIELDS = ("title", "authors", "year", "journal", "doi", "zotero_key", "source_id")
REQUIRED_FILES = ("source.pdf", "document.md", "parser/pages.jsonl", "parser/layout.json",
                  "page-map.json", "metadata.json", "quality.json")
IMAGE_RE = re.compile(r"!\[(?:\\.|[^\]\\])*\]\(\s*(<[^>]*>|(?:\\.|[^\s)])+)(?:\s+[^)]*)?\)")
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*?\bsrc\s*=\s*([\"'])(.*?)\1[^>]*>", re.I | re.S)
REFERENCE_IMAGE_RE = re.compile(r"!\[([^\]]*)\](?:\[([^\]]*)\])?")
REFERENCE_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)", re.M)


class BundleError(Exception):
    pass


def now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BundleError(f"Cannot read JSON {path.name}: {exc}") from exc


def parse_pages(spec: str | None, total: int) -> list[int]:
    if spec is None:
        return list(range(1, total + 1))
    result = []
    for part in spec.split(","):
        part = part.strip()
        if not re.fullmatch(r"\d+(?:-\d+)?", part):
            raise BundleError("--pages must use physical 1-based pages, e.g. 1-3,5")
        ends = [int(x) for x in part.split("-")]
        start, end = ends[0], ends[-1]
        if start < 1 or end > total or end < start:
            raise BundleError(f"Page selection {part} is outside PDF pages 1-{total}")
        for value in range(start, end + 1):
            if value in result:
                raise BundleError(f"Duplicate physical page in --pages: {value}")
            result.append(value)
    return sorted(result)


def image_references(markdown: str) -> list[str]:
    refs = [match.group(1).strip("<>") for match in IMAGE_RE.finditer(markdown)]
    refs += [html.unescape(match.group(2)) for match in HTML_IMAGE_RE.finditer(markdown)]
    # Inline image matches are excluded from reference-style processing.
    rest = IMAGE_RE.sub("", markdown)
    used = {(m.group(2) or m.group(1)).strip().casefold()
            for m in REFERENCE_IMAGE_RE.finditer(rest)}
    defs = {m.group(1).strip().casefold(): m.group(2).strip("<>")
            for m in REFERENCE_DEF_RE.finditer(markdown)}
    for key in used:
        if key not in defs:
            raise BundleError(f"Undefined image reference: [{key}]")
        refs.append(defs[key])
    return list(dict.fromkeys(refs))


def local_reference_path(ref: str) -> str:
    decoded = unquote(ref.replace("\\ ", " ")).replace("\\", "/")
    parsed = urlsplit(decoded)
    if parsed.scheme or parsed.netloc:
        raise BundleError(f"Image must be a supplied local asset, not a remote/data URL: {ref[:120]}")
    if parsed.query or parsed.fragment:
        raise BundleError(f"Image reference query/fragment is unsupported: {ref[:120]}")
    if not decoded or "\x00" in decoded:
        raise BundleError("Invalid empty or NUL-containing image path")
    return decoded


def normalise_markdown(markdown: str, mapping: dict[str, str]) -> str:
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    def replace_inline(match):
        token = match.group(1)
        ref = token.strip("<>")
        if ref not in mapping:
            return match.group(0)
        # Destinations use angle brackets when spaces are present.
        new = mapping[ref]
        if " " in new:
            new = f"<{new}>"
        return match.group(0)[:match.start(1) - match.start()] + new + match.group(0)[match.end(1) - match.start():]
    text = IMAGE_RE.sub(replace_inline, text)
    def replace_html(match):
        return match.group(0).replace(match.group(2), mapping.get(html.unescape(match.group(2)), match.group(2)), 1)
    text = HTML_IMAGE_RE.sub(replace_html, text)
    def replace_definition(match):
        ref = match.group(2).strip("<>")
        if ref not in mapping:
            return match.group(0)
        new = mapping[ref]
        if " " in new:
            new = f"<{new}>"
        return match.group(0)[:match.start(2) - match.start()] + new
    return REFERENCE_DEF_RE.sub(replace_definition, text)


def compose_document(pages: list[dict], asset_map: dict[str, str]) -> tuple[str, list[dict]]:
    lines = []
    page_map = []
    for item in pages:
        page_number = item["page_number"]
        marker_line = len(lines) + 1
        lines.append(f"<!-- pdf-page: {page_number} -->\n")
        markdown = normalise_markdown(item["markdown"], asset_map)
        content = markdown.splitlines(keepends=True)
        if content and not content[-1].endswith("\n"):
            content[-1] += "\n"
        start = len(lines) + 1 if content else None
        lines.extend(content)
        end = len(lines) if content else None
        lines.append("\n")
        page_map.append({"page_number": page_number, "page_label": item.get("page_label"),
                         "marker_line": marker_line, "content_start_line": start,
                         "content_end_line": end, "location_basis": item["location_basis"],
                         "l0_verified": False, "quote_verified": False})
    return "".join(lines), page_map


def file_manifest(root: Path) -> dict:
    return {str(path.relative_to(root).as_posix()): {"sha256": sha256(path), "size_bytes": path.stat().st_size}
            for path in sorted(root.rglob("*")) if path.is_file() and path.name != "conversion.json"}


def visible_text(markdown: str) -> str:
    text = re.sub(r"<!--.*?-->", "", markdown, flags=re.S)
    text = IMAGE_RE.sub("", text)
    text = HTML_IMAGE_RE.sub("", text)
    text = REFERENCE_DEF_RE.sub("", text)
    text = REFERENCE_IMAGE_RE.sub("", text)
    return "".join(char for char in text if char.isalnum())
