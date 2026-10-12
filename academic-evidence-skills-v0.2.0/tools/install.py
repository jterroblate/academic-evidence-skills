#!/usr/bin/env python3
"""Copy selected skills into an explicit destination. Preview by default; never overwrite."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
from doctor import check_integrity


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--destination', type=Path, required=True, help='Explicit skill directory for your client')
    ap.add_argument('--skills', nargs='+', required=True, help='Skill folder names, or all')
    ap.add_argument('--apply', action='store_true', help='Actually copy; omitted means preview only')
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest, errors = check_integrity(root)
    if errors:
        print(json.dumps({'status': 'invalid_package', 'errors': errors}, ensure_ascii=False, indent=2))
        return 1
    available = {s['name'] for s in manifest['skills']}
    names = sorted(available) if args.skills == ['all'] else args.skills
    if len(names) != len(set(names)) or not set(names) <= available:
        print(json.dumps({'status': 'invalid_selection', 'available': sorted(available)}, ensure_ascii=False))
        return 1
    destination = args.destination.expanduser().resolve()
    try:
        destination.relative_to(root)
        print('Destination must be outside the delivery package.')
        return 1
    except ValueError:
        pass
    conflicts = [str(destination / n) for n in names if (destination / n).exists() or (destination / n).is_symlink()]
    if conflicts or (destination.exists() and not destination.is_dir()):
        print(json.dumps({'status': 'refused_existing_target', 'conflicts': conflicts}, ensure_ascii=False))
        return 1
    plan = {'status': 'preview', 'destination': str(destination), 'skills': names,
            'note': 'Only copies skill files. Does not install runtimes, call APIs, or change client settings.'}
    if not args.apply:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    created = []
    destination.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='.academic-skills-stage-', dir=destination) as temp:
            for name in names:
                staged = Path(temp) / name
                shutil.copytree(root / 'skills' / name, staged, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            for name in names:
                target = destination / name
                # mkdir is the no-clobber reservation; a concurrent existing directory is never replaced.
                target.mkdir()
                created.append(target)
                for child in (Path(temp) / name).iterdir():
                    shutil.move(str(child), str(target / child.name))
    except Exception as exc:
        for target in reversed(created):
            shutil.rmtree(target)
        print(json.dumps({'status': 'failed_rolled_back', 'error': str(exc)}, ensure_ascii=False))
        return 1
    plan['status'] = 'installed'
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
