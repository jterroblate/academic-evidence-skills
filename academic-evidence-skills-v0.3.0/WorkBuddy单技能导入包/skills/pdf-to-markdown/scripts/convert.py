#!/usr/bin/env python3
"""Create a local, source-linked PDF -> Markdown bundle atomically."""
from __future__ import annotations

import argparse
import contextlib
import importlib.metadata
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from bundle import (BundleError, META_FIELDS, SCHEMA_VERSION, compose_document,
                    file_manifest, image_references, local_reference_path, now,
                    parse_pages, read_json, sha256, visible_text, write_json)


def open_pdf(path: Path):
    try:
        import pymupdf
    except ImportError as exc:
        raise BundleError("PyMuPDF is required. Install the pinned local dependencies in an isolated environment.") from exc
    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        raise BundleError(f"Cannot open source PDF: {exc}") from exc
    if not doc.is_pdf:
        doc.close()
        raise BundleError("The source must be a PDF, not another supported image/document type")
    if doc.needs_pass:
        doc.close()
        raise BundleError("This PDF is encrypted. Supply an authorised decrypted copy; passwords are not accepted by this script.")
    if len(doc) == 0:
        doc.close()
        raise BundleError("The PDF has no pages")
    return doc


def inspect_pdf(doc, selected: list[int]) -> dict:
    counts = []
    pages = []
    for index in range(len(doc)):
        page = doc[index]
        text = page.get_text("text")
        count = sum(not char.isspace() for char in text)
        # This is a scan-suspicion heuristic, not proof that source text is missing.
        page_area = page.rect.width * page.rect.height
        image_ratios = []
        for image in page.get_image_info():
            import pymupdf
            rect = pymupdf.Rect(image["bbox"]) & page.rect
            image_ratios.append(max(0.0, rect.width * rect.height) / page_area)
        largest_image_ratio = max(image_ratios, default=0.0)
        counts.append({"page_number": index + 1, "page_label": page.get_label() or None,
                       "native_text_chars": count, "largest_image_area_ratio": round(largest_image_ratio, 6)})
        if index + 1 in selected:
            blocks = [{"block_number": block[5], "bbox": list(block[:4]), "text": block[4]}
                      for block in page.get_text("blocks") if block[6] == 0]
            parallel_regions = []
            long_blocks = [block for block in blocks if sum(not char.isspace() for char in block["text"]) >= 25
                           and block["bbox"][3] - block["bbox"][1] >= 24]
            for left in long_blocks:
                for right in long_blocks:
                    a, b = left["bbox"], right["bbox"]
                    overlap = min(a[3], b[3]) - max(a[1], b[1])
                    min_height = min(a[3] - a[1], b[3] - b[1])
                    if a[2] < page.rect.width / 2 < b[0] and b[0] - a[2] >= page.rect.width * 0.10 and overlap >= min_height * 0.50:
                        parallel_regions.append([left["block_number"], right["block_number"]])
            pages.append({"page_number": index + 1, "page_label": page.get_label() or None,
                          "width": page.rect.width, "height": page.rect.height,
                          "native_text_chars": count, "largest_image_area_ratio": round(largest_image_ratio, 6),
                          "text_blocks": blocks, "parallel_text_regions_heuristic": parallel_regions})
    return {"schema_version": SCHEMA_VERSION, "engine": "PyMuPDF native PDF text extraction",
            "coordinate_space": "PDF points; origin top-left; native page coordinates",
            "md_coordinate_alignment": "not_established",
            "note": "These are native PDF text blocks, not word-by-word Markdown coordinates or parser alignment.",
            "pdf_metadata": doc.metadata, "source_page_count": len(doc),
            "preflight_all_pages": counts, "pages": pages}


def external_pages(path: Path, source_hash: str, selected: list[int], total: int):
    raw = read_json(path)
    if not isinstance(raw, dict) or raw.get("source_sha256") != source_hash:
        raise BundleError("External parser source_sha256 does not match this source PDF")
    engine = raw.get("engine")
    if not isinstance(engine, dict) or not all(isinstance(engine.get(key), str) and engine[key].strip()
                                               for key in ("name", "version")):
        raise BundleError("External parser input requires engine.name and engine.version (use 'unknown' if unavailable)")
    if "parameters" in engine and not isinstance(engine["parameters"], dict):
        raise BundleError("engine.parameters must be a JSON object")
    items = raw.get("pages")
    if not isinstance(items, list):
        raise BundleError("External parser input requires a pages array")
    seen = {}
    for item in items:
        if not isinstance(item, dict):
            raise BundleError("Every external parser page must be an object")
        number = item.get("page_number")
        if type(number) is not int or not 1 <= number <= total:
            raise BundleError(f"External page_number must be a physical integer within 1-{total}: {number}")
        if number in seen:
            raise BundleError(f"Duplicate external physical page_number: {number}")
        if not isinstance(item.get("markdown"), str):
            raise BundleError(f"External page {number} requires a markdown string")
        seen[number] = item
    missing = sorted(set(selected) - set(seen))
    if missing:
        raise BundleError(f"External parser input lacks selected source pages: {missing}. Use --pages only for an intended partial conversion.")
    return raw, [seen[number] for number in selected], {**engine, "parameters": engine.get("parameters", {})}


def local_pages(doc, selected: list[int], stage: Path):
    try:
        import pymupdf4llm
    except ImportError as exc:
        raise BundleError("PyMuPDF4LLM is required for the local trial route. Existing parser pages can be used with --parser-pages.") from exc
    pymupdf4llm.use_layout(False)
    # The classic route has no OCR implementation. use_ocr=False is explicit;
    # current classic versions may report this flag as ignored, without enabling OCR.
    with contextlib.chdir(stage), contextlib.redirect_stdout(sys.stderr):
        result = pymupdf4llm.to_markdown(doc, pages=[page - 1 for page in selected],
                                       page_chunks=True, write_images=True, image_path="assets",
                                       filename="source.pdf", show_progress=False,
                                       use_ocr=False, force_text=True)
    if not isinstance(result, list) or len(result) != len(selected):
        raise BundleError("Local parser did not return one chunk for every selected physical page")
    pages = []
    for number, chunk in zip(selected, result):
        if not isinstance(chunk, dict) or not isinstance(chunk.get("text"), str):
            raise BundleError("Local parser returned an unexpected page chunk schema")
        metadata = chunk.get("metadata", {})
        actual_page = metadata.get("page", metadata.get("page_number")) if isinstance(metadata, dict) else None
        if type(actual_page) is not int or actual_page != number:
            raise BundleError(f"Local parser page mapping mismatch: selected physical page {number}, returned {actual_page}")
        pages.append({"page_number": number, "markdown": chunk["text"],
                      "parser_metadata": metadata})
    engine = {"name": "pymupdf4llm-classic", "version": importlib.metadata.version("pymupdf4llm"),
              "pymupdf_version": importlib.metadata.version("pymupdf"),
              "parameters": {"use_layout": False, "use_ocr": False, "ocr_available_in_classic": False,
                             "page_chunks": True, "write_images": True, "force_text": True,
                             "physical_pages": selected}}
    return pages, engine


def assets_for(pages, stage: Path, external_input: Path | None, assets_dir: Path | None) -> dict:
    result = {}
    supplied_root = assets_dir.resolve() if assets_dir else (external_input.parent.resolve() if external_input else stage.resolve())
    for page in pages:
        for ref in image_references(page["markdown"]):
            decoded = local_reference_path(ref)
            path = Path(decoded)
            if path.is_absolute():
                if not assets_dir:
                    raise BundleError("Absolute external asset references require explicit --assets directory")
                origin = path.resolve()
            else:
                origin = (supplied_root / path).resolve()
            # An explicit assets folder accepts paths both relative to that folder
            # and conventionally prefixed with assets/ or images/.
            if not origin.is_file() and assets_dir and not path.is_absolute() and len(path.parts) > 1:
                origin = (supplied_root / Path(*path.parts[1:])).resolve()
            if not origin.is_relative_to(supplied_root) or not origin.is_file():
                raise BundleError(f"Missing asset or asset path escapes supplied root: {ref[:160]}")
            if origin.is_symlink():
                raise BundleError("Symlinked source assets are unsupported")
            digest = sha256(origin)
            suffix = origin.suffix.lower()
            if suffix not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".tiff", ".tif"):
                raise BundleError(f"Unsupported image asset extension: {suffix}")
            target_rel = "assets/" + digest[:24] + suffix
            target = stage / target_rel
            target.parent.mkdir(exist_ok=True)
            if origin != target:
                shutil.copyfile(origin, target)
            result[ref] = target_rel
    return result


def metadata_from(path: Path | None) -> tuple[dict, list[str]]:
    result = {key: None for key in META_FIELDS}
    if path is None:
        return result, []
    raw = read_json(path)
    if not isinstance(raw, dict):
        raise BundleError("--metadata must contain a JSON object")
    unknown = set(raw) - set(META_FIELDS)
    if unknown:
        raise BundleError(f"Unknown metadata fields: {sorted(unknown)}")
    for key, value in raw.items():
        if value is None:
            continue
        if key == "authors":
            if not isinstance(value, list) or not all(isinstance(name, str) for name in value):
                raise BundleError("metadata.authors must be a list of supplied author names, or null")
        elif key == "year":
            if type(value) not in (int, str):
                raise BundleError("metadata.year must be a supplied year integer/string, or null")
        elif not isinstance(value, str):
            raise BundleError(f"metadata.{key} must be a supplied string, or null")
        result[key] = value
    return result, [key for key, value in raw.items() if value is not None]


def convert(args) -> dict:
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().absolute()
    if not source.is_file():
        raise BundleError("Source PDF does not exist")
    if output.exists() or output.is_symlink():
        raise BundleError(f"Output already exists; refusing to overwrite: {output}")
    metadata, supplied_fields = metadata_from(args.metadata)
    source_hash = sha256(source)
    doc = open_pdf(source)
    stage = None
    lock = output.parent / ("." + output.name + ".pdf-to-markdown.lock")
    lock_acquired = False
    try:
        selected = parse_pages(args.pages, len(doc))
        layout = inspect_pdf(doc, selected)
        external = None
        if args.parser_pages:
            external, parsed, engine = external_pages(args.parser_pages.resolve(), source_hash, selected, len(doc))
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(descriptor)
            lock_acquired = True
        except FileExistsError as exc:
            raise BundleError(f"Another conversion has reserved this output: {lock}") from exc
        if output.exists() or output.is_symlink():
            raise BundleError("Output appeared during conversion; refusing to overwrite")
        stage = Path(tempfile.mkdtemp(prefix="." + output.name + ".incomplete-", dir=output.parent))
        (stage / "parser").mkdir()
        shutil.copyfile(source, stage / "source.pdf")
        if sha256(stage / "source.pdf") != source_hash:
            raise BundleError("Source changed while it was being copied; no bundle published")
        if args.parser_pages:
            shutil.copyfile(args.parser_pages, stage / "parser/external-input.json")
            provenance = external.get("provenance", "unknown")
            derivation = external.get("derivation", "unknown")
            location_basis = "parser_claimed_physical_page; not_L0_verified"
        else:
            parsed, engine = local_pages(doc, selected, stage)
            provenance = "local_source_pdf"
            derivation = "parser_raw"
            location_basis = "local_selected_physical_page; not_word_alignment"
        labels = {item["page_number"]: item["page_label"] for item in layout["preflight_all_pages"]}
        native_counts = {item["page_number"]: item["native_text_chars"] for item in layout["preflight_all_pages"]}
        image_ratios = {item["page_number"]: item["largest_image_area_ratio"] for item in layout["preflight_all_pages"]}
        pages = [{**item, "page_label": labels[item["page_number"]], "location_basis": location_basis,
                  "native_text_chars": native_counts[item["page_number"]]} for item in parsed]
        # Never carry parser assertions of quote/L0 verification into bundle metadata.
        for item in pages:
            item.pop("quote_verified", None)
            item.pop("l0_verified", None)
        asset_map = assets_for(pages, stage, args.parser_pages, args.assets)
        document, page_map = compose_document(pages, asset_map)
        (stage / "document.md").write_text(document, encoding="utf-8")
        with (stage / "parser/pages.jsonl").open("w", encoding="utf-8") as stream:
            for item in pages:
                stream.write(json.dumps(item, ensure_ascii=False) + "\n")
        write_json(stage / "parser/layout.json", layout)
        write_json(stage / "page-map.json", {"schema_version": SCHEMA_VERSION,
                   "numbering": "physical 1-based source PDF pages; labels are separate",
                   "coordinate_alignment": "not_established", "pages": page_map})
        write_json(stage / "metadata.json", metadata)
        issues = []
        native_missing = [number for number in selected if native_counts[number] == 0]
        empty = [item["page_number"] for item in pages if not visible_text(item["markdown"])]
        if empty:
            issues.append({"code": "missing_parser_text", "pages": empty,
                           "message": "Selected pages have no usable parsed text. Blank pages and scans require review; no OCR was run."})
        if not args.parser_pages and native_missing:
            issues.append({"code": "no_native_text", "pages": native_missing,
                           "message": "Local classic mode has no OCR. Supply existing OCR/parser pages or review scan/blank pages."})
        sparse = [number for number in selected if 0 < native_counts[number] < 40]
        scan_suspect = [number for number in selected if image_ratios[number] >= 0.65 and native_counts[number] < 200]
        if not args.parser_pages and (sparse or scan_suspect):
            issues.append({"code": "native_text_or_scan_suspicion_heuristic",
                           "pages": sorted(set(sparse + scan_suspect)), "heuristic": True,
                           "message": "Low native text or a dominant image suggests a scan/short page. This is a review trigger, not proof of missing text; no OCR was run."})
        parallel_pages = [item["page_number"] for item in layout["pages"] if item["parallel_text_regions_heuristic"]]
        if not args.parser_pages and parallel_pages:
            issues.append({"code": "parallel_text_columns_heuristic", "pages": parallel_pages, "heuristic": True,
                           "message": "Native text has separated parallel regions that may be columns. Local classic reading order must be compared with the PDF; this heuristic does not establish the correct order."})
        if args.parser_pages and (provenance in (None, "", "unknown") or derivation in (None, "", "unknown")):
            issues.append({"code": "unknown_external_derivation", "message": "External provenance/derivation was not declared; parser text must be reviewed."})
        if args.parser_pages and derivation != "parser_raw":
            issues.append({"code": "derived_external_text", "message": "External text may contain OCR or LLM edits. Source comparison is required before quotations/EU use."})
        formula_requirement = "latex" if getattr(args, "require_latex", False) else "not_specified"
        if formula_requirement == "latex":
            issues.append({"code": "formula_source_review_required", "pages": selected,
                           "message": "LaTeX was requested. Conversion and syntax checks do not verify mathematical fidelity; compare formulas with their source regions before accepting this requirement."})
        partial = selected != list(range(1, len(doc) + 1))
        status = "needs_review" if issues else ("partial" if partial else "complete")
        quality = {"schema_version": SCHEMA_VERSION, "checked_at": now(), "status": status,
                   "check_type": "machine_structure_and_integrity_only", "semantic_fidelity": "not_verified",
                   "formula_requirement": formula_requirement, "formula_fidelity": "not_verified",
                   "quote_verified": False, "l0_verified": False, "eu_ready": False,
                   "issues": issues, "native_no_text_selected_pages": native_missing,
                   "missing_parser_text_pages": empty,
                   "asset_reference_count": len(asset_map), "scope_partial": partial,
                   "preflight_heuristics": {"not_a_missing_text_proof": True,
                                            "low_native_text_chars_below": 40,
                                            "dominant_single_image_area_ratio_at_least": 0.65,
                                            "dominant_image_native_text_chars_below": 200,
                                            "low_native_text_selected_pages": sparse,
                                            "scan_suspect_selected_pages": scan_suspect,
                                            "parallel_text_selected_pages": parallel_pages,
                                            "parallel_text_rule": "Two multiline native text blocks on opposite sides of the page centre, >=10% page-width gap and >=50% vertical overlap; a review trigger only."},
                   "limitations": ["No semantic fidelity, OCR accuracy, formula/table accuracy or citation verification.",
                                   "Native bbox data is not Markdown word-coordinate alignment.",
                                   "External page positions are parser claims, not L0 verified coordinates.",
                                   "Do not use converted text directly as verified quotations or EU evidence."]}
        write_json(stage / "quality.json", quality)
        conversion = {"schema_version": SCHEMA_VERSION, "created_at": now(), "status": status,
                      "source_name": source.name, "source_sha256": source_hash,
                      "source_page_count": len(doc), "selected_pages": selected, "covered_pages": selected,
                      "coverage": {"partial": partial, "full_source": not partial},
                      "engine": engine, "provenance": provenance, "derivation": derivation,
                      "formula_requirement": formula_requirement, "formula_fidelity": "not_verified",
                      "metadata_supplied_fields": supplied_fields,
                      "asset_path_mapping": asset_map, "document_derivation": "deterministic page markers, LF line endings and local asset paths only",
                      "l0_verified": False, "quote_verified": False,
                      "artifacts": file_manifest(stage), "manifest_excludes": ["conversion.json"],
                      "integrity_note": "Hashes detect accidental changes; this unsigned manifest does not prove authenticity."}
        write_json(stage / "conversion.json", conversion)
        from verify import verify_bundle
        verification = verify_bundle(stage)
        if verification["errors"]:
            raise BundleError("Generated bundle failed machine verification: " + "; ".join(verification["errors"]))
        if output.exists() or output.is_symlink():
            raise BundleError("Output appeared before publication; refusing to overwrite")
        stage.rename(output)
        stage = None
        return {"output": str(output), "status": status, "source_page_count": len(doc),
                "selected_pages": selected, "issues": issues}
    finally:
        doc.close()
        if stage is not None:
            shutil.rmtree(stage, ignore_errors=True)
        if lock_acquired:
            lock.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New bundle directory; existing directories are never overwritten")
    parser.add_argument("--pages", help="Physical 1-based pages/ranges, e.g. 1-3,5; a subset is labelled partial")
    parser.add_argument("--parser-pages", type=Path, help="Existing parser page JSON with engine, source_sha256 and pages")
    parser.add_argument("--assets", type=Path, help="Explicit root containing referenced external image files")
    parser.add_argument("--metadata", type=Path, help="Supplied metadata JSON; unknown fields remain null")
    parser.add_argument("--require-latex", action="store_true", help="Record the LaTeX requirement and keep needs_review until separate source-formula review; this flag does not run formula OCR")
    args = parser.parse_args()
    if args.assets and not args.parser_pages:
        parser.error("--assets is only for existing external parser pages")
    try:
        result = convert(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 3 if result["status"] == "needs_review" else 0
    except (BundleError, OSError, ValueError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
