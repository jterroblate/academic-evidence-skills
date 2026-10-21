#!/usr/bin/env python3
"""Offline lexical math triage. Does not compile TeX or verify source fidelity."""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


class InputError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError(message)


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def read_object(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise InputError(f"{path.name} must contain a JSON object")
    return value


def escaped(text, index):
    count = 0
    while index > 0 and text[index - 1] == "\\":
        count += 1
        index -= 1
    return count % 2 == 1


def blank(text):
    return "".join("\n" if c == "\n" else " " for c in text)


def strip_tex_comments(text):
    chars, i = list(text), 0
    while i < len(text):
        if text[i] == "%" and not escaped(text, i):
            end = text.find("\n", i)
            end = len(text) if end < 0 else end
            chars[i:end] = blank(text[i:end])
            i = end
        else:
            i += 1
    return "".join(chars)


def mask_code(text):
    """Preserve offsets/newlines while excluding fenced and inline code."""
    chunks, fence = [], None
    tick = chr(96)
    pattern = re.compile(r"^ {0,3}([" + tick + r"~])\1{2,}(.*)$")
    for line in text.splitlines(keepends=True):
        match = pattern.match(line)
        if fence:
            chunks.append(blank(line))
            if match and match[1] == fence[0]:
                run = len(line.lstrip()) - len(line.lstrip().lstrip(fence[0]))
                if run >= fence[1] and not match[2].strip():
                    fence = None
        elif match:
            run = len(line.lstrip()) - len(line.lstrip().lstrip(match[1]))
            fence = (match[1], run)
            chunks.append(blank(line))
        else:
            chunks.append(line)
    visible = "".join(chunks)
    chars, i = list(visible), 0
    while i < len(visible):
        if visible[i] != tick or escaped(visible, i):
            i += 1
            continue
        end = i + 1
        while end < len(visible) and visible[end] == tick:
            end += 1
        run = visible[i:end]
        closing = re.search(r"(?<!" + tick + ")" + run + r"(?!" + tick + ")", visible[end:])
        if closing:
            stop = end + closing.end()
            chars[i:stop] = blank(visible[i:stop])
            i = stop
        else:
            i = end
    # HTML comments (including page markers) are not mathematical content.
    visible = "".join(chars)
    return re.sub(r"<!--.*?-->", lambda m: blank(m[0]), visible, flags=re.S)


def verify_bundle(root):
    if not root.is_dir():
        raise InputError("Bundle directory does not exist")
    paths = {name: root / name for name in
             ("source.pdf", "document.md", "conversion.json", "page-map.json")}
    for name, path in paths.items():
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            raise InputError(f"Missing, symlinked, or unsafe bundle file: {name}")
    conversion, mapping = read_object(paths["conversion.json"]), read_object(paths["page-map.json"])
    manifest = conversion.get("artifacts")
    if not isinstance(manifest, dict):
        raise InputError("conversion.json lacks artifacts manifest")
    checked = {}
    for name in ("source.pdf", "document.md", "page-map.json"):
        entry = manifest.get(name)
        actual = digest(paths[name])
        if not isinstance(entry, dict) or entry.get("sha256") != actual:
            raise InputError(f"SHA256 mismatch or missing manifest entry: {name}")
        if type(entry.get("size_bytes")) is not int or entry["size_bytes"] != paths[name].stat().st_size:
            raise InputError(f"Size mismatch or missing size_bytes: {name}")
        checked[name] = {"sha256": actual, "size_bytes": paths[name].stat().st_size}
    if conversion.get("source_sha256") != checked["source.pdf"]["sha256"]:
        raise InputError("conversion.source_sha256 does not match source.pdf")
    with paths["source.pdf"].open("rb") as stream:
        if not stream.read(1024).lstrip().startswith(b"%PDF-"):
            raise InputError("source.pdf lacks a PDF header (not a complete PDF validation)")
    text = paths["document.md"].read_text(encoding="utf-8")
    lines = text.splitlines()
    pages, total = mapping.get("pages"), conversion.get("source_page_count")
    if not isinstance(pages, list) or not pages or type(total) is not int or total < 1:
        raise InputError("Invalid page-map.pages or conversion.source_page_count")
    seen, previous_end = set(), 0
    for page in pages:
        if not isinstance(page, dict):
            raise InputError("Page-map entries must be objects")
        number, marker = page.get("page_number"), page.get("marker_line")
        start, end = page.get("content_start_line"), page.get("content_end_line")
        if (type(number) is not int or not 1 <= number <= total or number in seen
                or type(marker) is not int or not previous_end < marker <= len(lines)
                or lines[marker - 1].strip() != f"<!-- pdf-page: {number} -->"):
            raise InputError("Invalid, duplicate, or mismatched physical page marker")
        if start is None and end is None:
            previous_end = marker
        elif (type(start) is int and type(end) is int
              and start == marker + 1 and start <= end <= len(lines)):
            previous_end = end
        else:
            raise InputError("Invalid page-map content line range")
        seen.add(number)
    markers = [(i, int(m[1])) for i, line in enumerate(lines, 1)
               if (m := re.fullmatch(r"<!-- pdf-page: ([1-9]\d*) -->", line.strip()))]
    if markers != [(p["marker_line"], p["page_number"]) for p in pages]:
        raise InputError("Document page markers and page-map disagree")
    return text, pages, checked


def scan(text, pages):
    visible = mask_code(text)
    line_starts = [0] + [m.end() for m in re.finditer("\n", text)]
    line_at = lambda offset: bisect.bisect_right(line_starts, offset)
    page_boundaries = [line_starts[p["marker_line"] - 1] for p in pages]

    def physical(line):
        return next((p["page_number"] for p in pages
                     if p["content_start_line"] is not None
                     and p["content_start_line"] <= line <= p["content_end_line"]), None)

    issues, segments, masked = [], [], list(visible)

    def issue(code, offset, message):
        line = line_at(offset)
        issues.append({"code": code, "line": line, "physical_page": physical(line),
                       "message": message})

    # These were observed in real formula-rich parser output; do not repair by guessing.
    for offset, char in enumerate(visible):
        if ord(char) < 32 and char not in "\n\r\t":
            issue("unexpected_control_character", offset,
                  f"Unexpected U+{ord(char):04X}; compare the source glyph rather than substituting it")
        elif char == "\ufffd":
            issue("replacement_character", offset, "Replacement glyph U+FFFD may hide a lost source symbol")
    for match in re.finditer(r"<!--\s*(?:image|figure)(?:\s+placeholder)?\s*-->", text, re.I):
        issue("unresolved_document_image_placeholder", match.start(),
              "Image placeholder has no actual image reference; inspect whether a figure or formula is missing")

    def braces(content, offset):
        stack, i = [], 0
        while i < len(content):
            char = content[i]
            if char == "%" and not escaped(content, i):
                end = content.find("\n", i)
                i = len(content) if end < 0 else end + 1
                continue
            if not escaped(content, i):
                if char == "{":
                    stack.append(i)
                elif char == "}":
                    if stack:
                        stack.pop()
                    else:
                        issue("unmatched_closing_brace", offset + i, "Unmatched TeX closing brace")
            i += 1
        for index in stack:
            issue("unmatched_opening_brace", offset + index, "Unmatched TeX opening brace")

    i = 0
    while i < len(visible):
        opener = next((d for d in ("$$", r"\(", r"\[", "$")
                       if visible.startswith(d, i) and not escaped(visible, i)), None)
        if not opener:
            if any(visible.startswith(d, i) and not escaped(visible, i) for d in (r"\)", r"\]")):
                issue("unmatched_closing_delimiter", i, "Math closing delimiter has no opener")
                i += 2
            else:
                i += 1
            continue
        closer = {r"\(": r"\)", r"\[": r"\]"}.get(opener, opener)
        start, j = i, i + len(opener)
        # A damaged delimiter must not consume the next physical page's math.
        # This is diagnostic resynchronisation, not a repair of the source text.
        next_page = bisect.bisect_right(page_boundaries, start)
        boundary = page_boundaries[next_page] if next_page < len(page_boundaries) else len(visible)
        while j < boundary:
            if visible[j] == "%" and not escaped(visible, j):
                newline = visible.find("\n", j)
                j = boundary if newline < 0 else min(boundary, newline + 1)
                continue
            if visible.startswith(closer, j) and not escaped(visible, j):
                # An inline-dollar closer is not one half of a display pair.
                if closer != "$" or not visible.startswith("$$", j):
                    break
                j += 2
            elif any(visible.startswith(d, j) and not escaped(visible, j)
                     for d in (r"\)", r"\]")):
                issue("mismatched_math_delimiter", j, "Wrong-style math closing delimiter")
                j += 2
            else:
                j += 1
        if j >= boundary:
            issue("unclosed_math_delimiter", start, f"Unclosed math delimiter {opener}")
            if boundary < len(visible):
                issue("cross_page_math_segment", start,
                      "Unclosed math would cross a physical-page marker; stopped here and resumed scanning the next page")
            masked[start:boundary] = blank(visible[start:boundary])
            i = boundary
            continue
        stop = j + len(closer)
        content = visible[start + len(opener):j]
        clean = strip_tex_comments(content).strip()
        start_line, end_line = line_at(start), line_at(stop - 1)
        segment_pages = sorted({physical(line) for line in range(start_line, end_line + 1)
                                if physical(line) is not None})
        if not clean:
            issue("empty_math_segment", start, "Empty/comment-only math segment is not LaTeX output")
        braces(content, start + len(opener))
        if len(segment_pages) > 1:
            issue("cross_page_math_segment", start, "Math segment crosses existing physical page markers")
        segments.append({"index": len(segments) + 1, "delimiter": opener,
                         "start_line": start_line, "end_line": end_line,
                         "physical_page": segment_pages[0] if len(segment_pages) == 1 else None,
                         "physical_pages": segment_pages, "nonempty": bool(clean),
                         "source_snippet": text[start:stop][:240]})
        masked[start:stop] = blank(visible[start:stop])
        i = stop
    remaining = "".join(masked)
    # Conservative triage, not formula recognition. Plain CO2/CO₂/NaCl alone is not flagged.
    raw_pattern = re.compile(
        r"\\(?:frac|sqrt|sum|int|prod|begin)\b|"
        r"\b[A-Za-z][A-Za-z0-9_()]{0,18}\s*(?:=|≈|≠|≤|≥|∝)\s*\S|"
        r"[Α-Ωα-ω]\s*(?:=|≈|≠|≤|≥|<|>)\s*\S|"
        r"[∑∏∫]\s*\S|(?:\[(?:formula|equation|math)[ _-]*(?:image|placeholder)?\])",
        re.I)
    for number, line in enumerate(remaining.splitlines(), 1):
        if raw_pattern.search(line):
            issues.append({"code": "raw_or_undelimited_math_candidate", "line": number,
                           "physical_page": physical(number),
                           "message": "Possible raw/undelimited formula or placeholder; compare source PDF",
                           "source_snippet": text.splitlines()[number - 1][:200]})
        if re.search(r"!\[[^\]]*(?:formula|equation|math|公式)[^\]]*\]\(", line, re.I):
            issues.append({"code": "formula_image_requires_review", "line": number,
                           "physical_page": physical(number),
                           "message": "Formula-labelled image is not verified LaTeX output"})
    return segments, issues


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--require-latex", action="store_true",
                        help="Exit 3 when no nonempty delimited math segment exists; not a coverage check")
    parser.add_argument("--output", required=True, type=Path,
                        help="New JSON report outside bundle; refuses overwrite")
    try:
        args = parser.parse_args(argv)
        root, output = args.bundle.resolve(), args.output.resolve()
        if output.is_relative_to(root):
            raise InputError("Report must be outside bundle to preserve its original manifest")
        if args.output.exists() or args.output.is_symlink():
            raise InputError("Output exists; refusing overwrite")
        text, pages, checked = verify_bundle(root)
        segments, issues = scan(text, pages)
        count = sum(s["nonempty"] for s in segments)
        if args.require_latex and count == 0:
            issues.append({"code": "latex_required_but_absent", "line": None,
                           "physical_page": None,
                           "message": "No nonempty delimited math segment; text baseline is not LaTeX output"})
        result = {
            "schema_version": "1.0", "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "needs_review" if issues else "lexical_checks_passed",
            "exit_code": 3 if issues else 0, "bundle": str(root),
            "integrity": {"checked_artifacts": checked,
                          "manifest_authenticity": "not_verified_unsigned_manifest",
                          "pdf_structure_validation": "header_only"},
            "syntax_check_scope": "basic_lexical", "latex_compilation": "not_performed",
            "scan_recovery": "reset_unclosed_math_at_next_physical_page_marker",
            "diagnostic_recovery": {
                "boundary_source": "existing page-map and physical-page markers",
                "resets": sum(i["code"] == "cross_page_math_segment" for i in issues),
                "source_text_repaired": False,
                "cross_page_math_still_requires_review": True,
                "coverage": "not_established"},
            "semantic": "not_verified", "source_math_fidelity": "not_verified",
            "source_review_required": True, "math_coverage": "not_established",
            "require_latex": args.require_latex, "nonempty_math_segments": count,
            "segments": segments, "issues": issues,
            "location_basis": "existing physical-page markers only; no glyph/bbox alignment",
            "evidence_promotion": {"quote_verified": False, "l0_verified": False, "eu_verified": False},
            "limitations": [
                "Not a full Markdown/TeX parser or compiler; no command/environment semantics.",
                "Unlabelled formula images, missing formulas and all-page coverage cannot be established.",
                "Raw-math heuristics can have false positives/negatives; Unicode or chemical names alone need not be TeX.",
                "A syntactically balanced but wrong exponent/denominator can pass; compare actual source PDF.",
                "Unclosed math stops at the next physical-page marker so later pages can be scanned; damaged-page coverage remains unknown.",
                "No network, model, external command or bundle mutation is performed."
            ]}
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(json.dumps({"status": result["status"], "report": str(output),
                          "math_segments": count, "issues": len(issues)}, ensure_ascii=False))
        return result["exit_code"]
    except (InputError, OSError, UnicodeError, ValueError, TypeError, KeyError, OverflowError) as exc:
        print(f"math_check: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
