#!/usr/bin/env python3
"""Offline inspection of preserved ScholarQA JSON; never verifies quotes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def inspect(path, exit_code):
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError('result must be a JSON object')
    errors = data.get('operation_errors', [])
    unresolved = data.get('unresolved_ids', [])
    if not isinstance(errors, list) or not isinstance(unresolved, list):
        raise ValueError('operation_errors and unresolved_ids must be arrays when present')
    top_error = data.get('error')
    if top_error:
        status = 'error'
    elif exit_code == 2:
        status = 'local-or-input-error'
    elif exit_code == 1 or errors or unresolved:
        status = 'partial'
    elif exit_code == 0:
        status = 'reported-success'
    else:
        status = 'unknown-process-status'
    return {'schema_version': 'academic-discovery-inspection-candidate/0.1',
            'kind': data.get('kind'), 'raw_artifact': str(Path(path)),
            'raw_sha256': hashlib.sha256(raw).hexdigest(),
            'exit_code': exit_code, 'status': status, 'operation_errors': errors,
            'top_level_error': top_error, 'unresolved_ids': unresolved,
            'search_queries': data.get('search_queries'),
            'candidate_paper_ids': data.get('candidate_paper_ids'),
            'identity_verification_scope': 'bibliographic-identity-only',
            'quote_verification': 'not-performed', 'formal_evidence_unit': False,
            'review_status': 'candidate'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('result_json')
    p.add_argument('--exit-code', type=int, choices=(0, 1, 2), required=True)
    a = p.parse_args()
    try:
        print(json.dumps(inspect(a.result_json, a.exit_code), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'error': str(exc), 'review_status': 'candidate'}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
