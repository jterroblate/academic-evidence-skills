#!/usr/bin/env python3
"""Recheck bundle integrity, physical page coverage and deterministic derivation."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from bundle import (BundleError, META_FIELDS, REQUIRED_FILES, compose_document,
                    image_references, local_reference_path, read_json, sha256)


def verify_bundle(root: Path) -> dict:
    errors = []
    warnings = []
    result = {"bundle": str(root), "status": "invalid", "errors": errors, "warnings": warnings,
              "semantic_fidelity": "not_verified", "quote_verified": False, "l0_verified": False, "eu_ready": False}
    try:
        if not root.is_dir():
            raise BundleError("Bundle directory does not exist")
        for name in (*REQUIRED_FILES, "conversion.json"):
            file = root / name
            if not file.is_file() or file.is_symlink():
                errors.append(f"Required regular file missing: {name}")
        if errors:
            return result
        conversion = read_json(root / "conversion.json")
        quality = read_json(root / "quality.json")
        page_map = read_json(root / "page-map.json")
        metadata = read_json(root / "metadata.json")
        layout = read_json(root / "parser/layout.json")
        if conversion.get("l0_verified") is not False or conversion.get("quote_verified") is not False:
            errors.append("Conversion must not claim L0 or quotation verification")
        if any(quality.get(key) is not False for key in ("l0_verified", "quote_verified", "eu_ready")):
            errors.append("Machine quality report must not claim L0, quotation or EU verification")
        manifest = conversion.get("artifacts", {})
        if not isinstance(manifest, dict):
            raise BundleError("Invalid artifacts manifest")
        actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
        expected = set(manifest) | {"conversion.json"}
        if actual != expected:
            errors.append(f"Artifact inventory mismatch: extra={sorted(actual-expected)}, missing={sorted(expected-actual)}")
        for name in REQUIRED_FILES:
            if name not in manifest:
                errors.append(f"Required artifact omitted from hashes: {name}")
        for name, info in manifest.items():
            path = root / name
            if Path(name).is_absolute() or not path.resolve().is_relative_to(root.resolve()) or path.is_symlink():
                errors.append(f"Unsafe artifact path: {name}")
                continue
            if not isinstance(info, dict) or not path.is_file():
                errors.append(f"Invalid or missing manifest artifact: {name}")
            elif sha256(path) != info.get("sha256") or path.stat().st_size != info.get("size_bytes"):
                errors.append(f"Artifact hash/size mismatch: {name}")
        source_hash = sha256(root / "source.pdf")
        if source_hash != conversion.get("source_sha256"):
            errors.append("Source PDF hash mismatch")
        try:
            import pymupdf
            with pymupdf.open(root / "source.pdf") as doc:
                if not doc.is_pdf or doc.needs_pass:
                    raise BundleError("Bundle source is not an accessible unencrypted PDF")
                total = len(doc)
                labels = {index + 1: doc[index].get_label() or None for index in range(total)}
        except ImportError as exc:
            raise BundleError("PyMuPDF is required to independently check the source page count") from exc
        if total != conversion.get("source_page_count") or total != layout.get("source_page_count"):
            errors.append("Source PDF page count does not match conversion/layout")
        selected = conversion.get("selected_pages")
        if not isinstance(selected, list) or not selected or any(type(number) is not int or not 1 <= number <= total for number in selected):
            raise BundleError("Selected pages are missing, non-integer or outside source bounds")
        if selected != sorted(set(selected)):
            errors.append("Selected pages are duplicated or out of physical order")
        if conversion.get("covered_pages") != selected:
            errors.append("Covered pages differ from the declared selected pages")
        partial = selected != list(range(1, total + 1))
        if conversion.get("coverage") != {"partial": partial, "full_source": not partial}:
            errors.append("Coverage partial/full declaration contradicts source pages")
        if partial != quality.get("scope_partial"):
            errors.append("Quality partial declaration contradicts source pages")
        raw_lines = (root / "parser/pages.jsonl").read_text(encoding="utf-8").splitlines()
        pages = [json.loads(line) for line in raw_lines if line.strip()]
        if [page.get("page_number") for page in pages] != selected:
            errors.append("Parser pages duplicate, omit or misorder selected physical pages")
        for page in pages:
            if not isinstance(page.get("markdown"), str):
                raise BundleError("Parser page markdown is not a string")
            if page.get("page_label") != labels.get(page.get("page_number")):
                errors.append(f"PDF page label mismatch for physical page {page.get('page_number')}")
            if page.get("l0_verified") is True or page.get("quote_verified") is True:
                errors.append("Parser pages must not claim verification")
        mapping = conversion.get("asset_path_mapping", {})
        document, expected_map = compose_document(pages, mapping)
        actual_document = (root / "document.md").read_text(encoding="utf-8")
        if actual_document != document:
            errors.append("document.md is not the deterministic derivation of raw parser pages")
        if page_map.get("pages") != expected_map:
            errors.append("Page-map line ranges/labels do not match deterministic document pages")
        lines = actual_document.splitlines()
        markers = [int(match.group(1)) for line in lines if (match := re.fullmatch(r"<!-- pdf-page: (\d+) -->", line))]
        if markers != selected:
            errors.append("Document physical page markers are duplicated or missing (including reserved markers in parser text)")
        for entry in page_map.get("pages", []):
            if not 1 <= entry.get("marker_line", 0) <= len(lines):
                errors.append("Page-map marker line is out of bounds")
            start, end = entry.get("content_start_line"), entry.get("content_end_line")
            if (start is None) != (end is None) or (start is not None and not 1 <= start <= end <= len(lines)):
                errors.append("Page-map content range is invalid or out of bounds")
        for ref in image_references(actual_document):
            path = root / local_reference_path(ref)
            if not path.resolve().is_relative_to(root.resolve()) or not path.is_file() or path.is_symlink():
                errors.append(f"Document image asset missing or unsafe: {ref}")
        if set(metadata) != set(META_FIELDS):
            errors.append("Metadata fields differ from the permitted supplied-field schema")
        supplied = conversion.get("metadata_supplied_fields", [])
        if any(value is not None and key not in supplied for key, value in metadata.items()):
            errors.append("Non-null metadata was not declared as supplied")
        status = conversion.get("status")
        if status not in ("complete", "partial", "needs_review") or quality.get("status") != status:
            errors.append("Invalid/inconsistent conversion and quality status")
        if status == "complete" and partial:
            errors.append("Partial conversion is falsely marked complete")
        if status == "partial" and not partial:
            errors.append("Full conversion is falsely marked partial")
        if quality.get("issues") and status != "needs_review":
            errors.append("Known review issues exist but bundle is marked as passed")
        if status == "needs_review":
            warnings.extend(issue.get("message", issue.get("code", "Review required")) for issue in quality.get("issues", []))
        warnings.append("Machine checks do not establish semantic fidelity, formula/table accuracy or verified citations/EU evidence.")
        result["status"] = "invalid" if errors else status
        result["source_page_count"] = total
        result["selected_pages"] = selected
    except (BundleError, OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append(str(exc))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--json", action="store_true", help="Print a JSON machine report (also the default)")
    args = parser.parse_args()
    result = verify_bundle(args.bundle.expanduser().resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else (3 if result["status"] == "needs_review" else 0)


if __name__ == "__main__":
    raise SystemExit(main())
