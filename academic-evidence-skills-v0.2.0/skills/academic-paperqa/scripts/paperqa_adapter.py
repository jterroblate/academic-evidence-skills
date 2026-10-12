#!/usr/bin/env python3
"""Optional PaperQA adapter. plan/doctor perform no backend requests."""
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from datetime import datetime, timezone


class InputError(ValueError):
    pass


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise InputError('JSON input must be an object')
    return data


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')


def load_sources(bundle):
    base = Path(bundle).resolve().parent
    sources = read_json(bundle).get('sources')
    if not isinstance(sources, list) or not sources:
        raise InputError('bundle.sources must be a non-empty array')
    found, normalized = set(), []
    for s in sources:
        if not isinstance(s, dict):
            raise InputError('each source must be an object')
        sid = s.get('source_id')
        if not isinstance(sid, str) or not sid.strip():
            raise InputError('source_id must come from the caller and be non-empty')
        if sid in found:
            raise InputError('duplicate source_id')
        found.add(sid)
        family = s.get('source_family')
        if family is not None and (not isinstance(family, str) or not family.strip()):
            raise InputError('source_family must be a caller value or null')
        expected = s.get('source_hash')
        if not isinstance(expected, str) or not re.fullmatch('[0-9a-fA-F]{64}', expected):
            raise InputError('source_hash must be a full 64-character SHA256')
        source_path = s.get('source_path')
        if not isinstance(source_path, str) or not source_path.strip():
            raise InputError('source_path must identify an existing local PDF')
        if '://' in source_path:
            raise InputError('remote sources are not accepted; use an existing local bundle')
        path = (base / source_path).resolve()
        if path.suffix.lower() != '.pdf' or not path.is_file():
            raise InputError('source must be an existing local .pdf')
        with path.open('rb') as f:
            if not f.read(1024).lstrip().startswith(b'%PDF-'):
                raise InputError('source lacks a PDF header')
        actual = sha(path)
        if actual != expected.lower():
            raise InputError('source_hash mismatch; original source may have changed')
        citation = s.get('bibliographic_citation')
        if not isinstance(citation, str) or not citation.strip():
            raise InputError('bibliographic_citation must be a caller citation or source label')
        normalized.append({'source_id': sid, 'source_family': family, 'source_path': str(path),
                           'source_hash': actual, 'bibliographic_citation': citation,
                           'pdf_page_1based': None, 'printed_page': None,
                           'review_status': 'candidate', 'locator_status': 'pending-L0-check'})
    return normalized


def validate_config(path):
    if path is None:
        return None, ['explicit backend config is missing']
    cfg = read_json(path)
    errors = []
    if cfg.get('backend_declared_ready') is not True:
        errors.append('LLM and embedding backend readiness has not been declared by caller')
    if cfg.get('content_submission_authorized') is not True:
        errors.append('document content submission to selected backend is not authorized')
    if cfg.get('backend_scope') not in ('local', 'existing-remote'):
        errors.append('backend_scope must be local or existing-remote')
    settings = cfg.get('settings')
    if not isinstance(settings, dict):
        return cfg, errors + ['config.settings must be an object']
    for key in ('llm', 'summary_llm', 'embedding'):
        if not isinstance(settings.get(key), str) or not settings[key].strip():
            errors.append('explicit ' + key + ' model is required; no library defaults')
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k.lower() in ('api_key', 'password', 'token', 'authorization') and v:
                    errors.append('embedded credentials are disallowed; use existing environment configuration')
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(settings)
    if not isinstance(settings.get('parsing', {}), dict):
        errors.append('settings.parsing must be an object')
    return cfg, errors


def safe_settings(cfg):
    settings = dict(cfg['settings'])
    settings['parsing'] = dict(settings.get('parsing', {}))
    settings['parsing'].update({'use_doc_details': False, 'multimodal': False})
    return settings


def doctor(config):
    cfg, issues = validate_config(config)
    if sys.version_info < (3, 11):
        issues.append('Python >=3.11 is required by paper-qa')
    try:
        available = importlib.util.find_spec('paperqa') is not None
    except (ImportError, ValueError):
        available = False
    if not available:
        issues.append('paper-qa library is not installed in this Python environment')
    else:
        try:
            from paperqa import Docs, Settings
            if not callable(Docs) or not callable(Settings):
                raise ImportError('Docs/Settings API missing')
            if cfg and isinstance(cfg.get('settings'), dict) and not issues:
                Settings(**safe_settings(cfg))
        except Exception as exc:
            issues.append('paperqa import/settings validation failed: ' + type(exc).__name__)
    return {'status': 'blocked-dependency-or-config' if issues else 'config-ready-unverified',
            'backend_tested': False, 'network_probe_performed': False,
            'backend_internal_retry_policy_tested': False,
            'paperqa_available': available, 'issues': issues, 'formal_evidence_unit': False}


def make_plan(bundle, question, config):
    if not question.strip():
        raise InputError('question must be non-empty')
    sources = load_sources(bundle)
    _, issues = validate_config(config)
    return {'schema_version': 'academic-paperqa-plan-candidate/0.1', 'mode': 'offline-plan',
            'question': question, 'content_nature': 'AI-derived-workflow-plan',
            'bundle_sha256': sha(bundle), 'source_count': len(sources), 'source_map': sources,
            'backend_config_issues': issues, 'model_calls_performed': False,
            'quote_verification': 'not-performed', 'formal_evidence_unit': False,
            'review_status': 'candidate'}


async def execute_query(sources, question, cfg, out, manifest):
    from paperqa import Docs, Settings
    settings = Settings(**safe_settings(cfg))
    docs = Docs()
    for source in sources:
        await docs.aadd(source['source_path'], citation=source['bibliographic_citation'],
                        docname=source['source_id'], settings=settings)
    session = await docs.aquery(question, settings=settings)
    manifest.update({'state': 'returned', 'returned_at': timestamp(), 'retry_allowed': False})
    save(out / 'run-manifest.json', manifest)
    if hasattr(session, 'model_dump'):
        save(out / 'session.raw.derived.json', session.model_dump(mode='json'))
    for source in sources:
        if sha(source['source_path']) != source['source_hash']:
            raise InputError('L0 changed during query; returned content retained, mapping invalid')
    mapping = {s['source_id']: s for s in sources}
    contexts, citations = [], []
    for context in getattr(session, 'contexts', []):
        text = getattr(context, 'text', None)
        sid = getattr(getattr(text, 'doc', None), 'docname', None)
        source = mapping.get(sid)
        contexts.append({'context_summary': getattr(context, 'context', None),
                         'content_nature': 'AI-derived', 'source_id': sid if source else None})
        citations.append({'source_id': sid if source else None,
                          'source_hash': source['source_hash'] if source else None,
                          'source_family': source['source_family'] if source else None,
                          'paperqa_docname': sid, 'excerpt_candidate': getattr(text, 'text', None),
                          'quote': None, 'pdf_page_1based': None, 'printed_page': None,
                          'locator_status': 'pending-L0-check' if source else 'unmapped',
                          'evidence_tier': None, 'review_status': 'candidate',
                          'formal_evidence_unit': False})
    save(out / 'answer.derived.json', {'content_nature': 'AI-derived', 'question': question,
          'answer': getattr(session, 'answer', None),
          'formatted_answer': getattr(session, 'formatted_answer', None),
          'context_summaries': contexts, 'review_status': 'candidate'})
    save(out / 'citations.candidate.json', {'schema_version': 'academic-citations-candidate/0.1',
          'citations': citations, 'quote_verification': 'not-performed', 'formal_evidence_unit': False})
    manifest.update({'state': 'completed', 'completed_at': timestamp()})
    save(out / 'run-manifest.json', manifest)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest='command', required=True)
    d = subs.add_parser('doctor'); d.add_argument('--config')
    for mode in ('plan', 'query'):
        s = subs.add_parser(mode); s.add_argument('--bundle', required=True)
        s.add_argument('--question', required=True); s.add_argument('--config')
        s.add_argument('--out', required=True)
        if mode == 'query':
            s.add_argument('--allow-model-calls', action='store_true')
    a = p.parse_args(argv)
    try:
        if a.command == 'doctor':
            report = doctor(a.config)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 3 if report['issues'] else 0
        plan = make_plan(a.bundle, a.question, a.config)
        if a.command == 'query':
            if not a.allow_model_calls:
                print(json.dumps({'status': 'blocked-config', 'issues': ['query requires explicit --allow-model-calls']}))
                return 3
            report = doctor(a.config)
            if report['issues']:
                print(json.dumps(report, ensure_ascii=False, indent=2))
                return 3
        out = Path(a.out).resolve()
        out.mkdir(parents=True, exist_ok=False)
        save(out / 'plan.json', plan)
        save(out / 'source-map.candidate.json', {'sources': plan['source_map'], 'formal_evidence_unit': False})
        if a.command == 'plan':
            print(json.dumps({'status': 'planned', 'out': str(out), 'model_calls_performed': False}, ensure_ascii=False))
            return 0
        cfg, _ = validate_config(a.config)
        manifest = {'state': 'started', 'started_at': timestamp(), 'bundle_sha256': sha(a.bundle),
                    'config_sha256': sha(a.config), 'backend_scope': cfg['backend_scope'],
                    'review_status': 'candidate', 'formal_evidence_unit': False,
                    'implicit_metadata_upgrade': False, 'media_enrichment': False,
                    'retry_scope': 'adapter-aquery-only; provider-internal-retries-unverified',
                    'retry_allowed': False}
        save(out / 'run-manifest.json', manifest)
        try:
            asyncio.run(execute_query(plan['source_map'], a.question, cfg, out, manifest))
        except Exception as exc:
            returned = 'returned_at' in manifest
            manifest.update({'state': 'returned-local-error' if returned else 'failed-or-unknown',
                             'error_type': type(exc).__name__, 'retry_allowed': False,
                             'note': 'Inspect existing return/call; do not automatically repeat model query.'})
            save(out / 'run-manifest.json', manifest)
            print(json.dumps({'status': manifest['state'], 'out': str(out)}, ensure_ascii=False))
            return 2
        print(json.dumps({'status': 'completed', 'out': str(out), 'formal_evidence_unit': False}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'status': 'local-or-input-error', 'error_type': type(exc).__name__, 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
