#!/usr/bin/env python3
"""Offline package integrity and optional runtime inventory; does not install anything."""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


def check_integrity(root):
    root = Path(root).resolve()
    errors = []
    manifest_path = root / 'manifest.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return {}, [f'manifest.json: {exc}']
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        return manifest, ['manifest.files must be a nonempty mapping']
    for p in root.rglob('*'):
        rel = p.relative_to(root).as_posix()
        if '__pycache__' in p.parts or p.suffix == '.pyc':
            continue
        if p.is_symlink():
            errors.append(f'Symlink not allowed in delivery: {rel}')
        elif p.is_file() and rel != 'manifest.json' and rel not in files:
            errors.append(f'Unlisted file: {rel}')
    for rel, expected in files.items():
        p = root / rel
        if Path(rel).is_absolute() or '..' in Path(rel).parts or p.is_symlink():
            errors.append(f'Unsafe path: {rel}')
            continue
        try:
            p.resolve().relative_to(root)
            actual = hashlib.sha256(p.read_bytes()).hexdigest()
            if actual != expected:
                errors.append(f'Hash mismatch: {rel}')
        except (OSError, ValueError) as exc:
            errors.append(f'Missing/unreadable: {rel}: {exc}')
    for skill in manifest.get('skills', []):
        name = skill.get('name', '')
        if not name or Path(name).name != name or name in {'.', '..'}:
            errors.append(f'Unsafe skill name: {name!r}')
            continue
        skill_path = root / 'skills' / name / 'SKILL.md'
        if not skill_path.is_file():
            errors.append(f'Missing SKILL.md: {name}')
    return manifest, errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--strict-dependencies', action='store_true', help='Also fail if an optional runtime command is absent')
    args = ap.parse_args()
    manifest, errors = check_integrity(args.root)
    runtime = []
    for item in manifest.get('runtime_commands', []):
        command = item['command']
        location = shutil.which(command)
        runtime.append({'command': command, 'available': bool(location), 'path': location,
                        'skills': item.get('skills', []), 'note': item.get('note')})
    result = {'integrity': 'pass' if not errors else 'fail', 'errors': errors,
              'runtime_commands': runtime, 'python': sys.version.split()[0],
              'network_calls': 0, 'backend_accuracy_tested': False,
              'note': 'Command presence is not model, API key, version, or backend readiness. Missing optional runtimes do not invalidate the skill files.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(errors) or (args.strict_dependencies and any(not x['available'] for x in runtime)))


if __name__ == '__main__':
    raise SystemExit(main())
