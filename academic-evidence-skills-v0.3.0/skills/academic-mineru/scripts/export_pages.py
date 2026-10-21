#!/usr/bin/env python3
"""Adapt an existing MinerU 4 native export into source-bound page JSON.

No parsing inference, model download, document edits or asset copying is performed.
Pass the native directory as convert.py --assets when consuming the result.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path


def sha256(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('native_dir', type=Path)
    ap.add_argument('--source', required=True, type=Path)
    ap.add_argument('--run-record', required=True, type=Path,
                    help='Existing producer record containing source_sha256, engine and actual_pages')
    ap.add_argument('--output', required=True, type=Path, help='New page JSON outside the native export')
    args = ap.parse_args()
    try:
        native = args.native_dir.resolve(strict=True)
        source = args.source.resolve(strict=True)
        record_path = args.run_record.resolve(strict=True)
        output = args.output.absolute()
        if output.exists() or output.is_symlink():
            raise ValueError('Refusing to overwrite output')
        if output.resolve().is_relative_to(native):
            raise ValueError('Output must be outside the preserved native export')
        record = json.loads(record_path.read_text(encoding='utf-8'))
        source_hash = sha256(source)
        if record.get('source_sha256') != source_hash:
            raise ValueError('Producer record source hash does not match the supplied PDF')
        engine = record.get('engine')
        if not isinstance(engine, dict) or not all(isinstance(engine.get(k), str) and engine[k] for k in ('name', 'version')):
            raise ValueError('Producer record lacks engine.name/version')
        middle_path = native / 'middle_json.json'
        if not middle_path.is_file() or middle_path.is_symlink():
            raise ValueError('A regular materialized middle_json.json is required')
        from mineru.parser import ParseResult
        sdk_version = importlib.metadata.version('mineru')
        if sdk_version.split('.')[0] != '4':
            raise ValueError('This adapter targets the MinerU 4 schema; check the installed SDK')
        parsed = ParseResult.from_json(middle_path.read_text(encoding='utf-8'))
        pages = []
        for page in parsed.pages:
            single = ParseResult(middle_json=parsed.middle_json.model_copy(deep=True))
            single.middle_json.pages = [page]
            markdown = single.markdown()
            if 'data:image' in markdown.lower():
                raise ValueError('Native export still embeds image data; materialize assets before adapting')
            pages.append({'page_number': page.page_idx + 1, 'markdown': markdown,
                          'native_page': page.model_dump(mode='json'),
                          'formula_review_status': 'not_verified'})
        actual = [p['page_number'] for p in pages]
        if not actual or actual != sorted(set(actual)) or actual != record.get('actual_pages'):
            raise ValueError('Physical pages disagree with the producer record or contain duplicates')
        if sha256(source) != source_hash:
            raise ValueError('Source changed while adapting')
        result = {'source_sha256': source_hash, 'engine': engine,
                  'provenance': 'local-adapter-of-existing-materialized-mineru-export',
                  'derivation': 'parser_raw', 'pages': pages, 'actual_pages': actual,
                  'source_total_pages': record.get('source_total_pages'),
                  'adapter': {'name': 'academic-mineru/export_pages.py',
                              'sdk_version': sdk_version, 'tested_sdk_version': '4.0.12',
                              'native_json_sha256': sha256(middle_path),
                              'producer_record_sha256': sha256(record_path),
                              'producer_authenticity': 'not_verified_unsigned_record'},
                  'formula_status': 'unreviewed_model_transcription',
                  'asset_root_note': 'Pass the original native directory as --assets; keep its assets unchanged'}
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        print(json.dumps({'output': str(output), 'physical_pages': actual,
                          'status': 'adapted_unreviewed'}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        ap.exit(1, f'export_pages: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
