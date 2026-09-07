"""Build documentation and the browser's matching Python package."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path = ROOT) -> None:
    """Run a required build step and preserve its failure status."""
    subprocess.run(args, cwd=cwd, check=True)


def stage(destination: Path) -> None:
    """Stage compiled modules, verified wheels and the shared Django app."""
    run('npm', 'ci', cwd=ROOT / 'playground')
    run('npm', 'run', 'build', cwd=ROOT / 'playground')
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'playground/dist', destination, dirs_exist_ok=True)
    wheels: list[dict[str, str]] = json.loads(
        (ROOT / 'playground/python-wheels.json').read_text()
    )
    staged: list[dict[str, str]] = []
    wheel_dir: Path = destination / 'wheels'
    wheel_dir.mkdir(exist_ok=True)
    for wheel in wheels:
        filename: str = wheel['url'].rsplit('/', 1)[-1]
        target: Path = wheel_dir / filename
        if not target.exists():
            with urllib.request.urlopen(wheel['url'], timeout=60) as response:
                target.write_bytes(response.read())
        digest: str = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != wheel['sha256']:
            raise ValueError(f'Wheel checksum mismatch: {filename}')
        staged.append({'url': f'wheels/{filename}', 'sha256': digest})
    with tempfile.TemporaryDirectory(prefix='tags-input-build-') as temporary:
        run('uv', 'build', '--wheel', '--out-dir', temporary)
        project_wheel: Path = next(Path(temporary).glob('*.whl'))
        shutil.copy2(project_wheel, wheel_dir)
        staged.append(
            {
                'url': f'wheels/{project_wheel.name}',
                'sha256': hashlib.sha256(
                    project_wheel.read_bytes()
                ).hexdigest(),
            }
        )
    sources: dict[str, str] = {
        path.relative_to(ROOT).as_posix(): path.read_text()
        for path in (ROOT / 'showcase').rglob('*')
        if path.is_file() and path.suffix in {'.py', '.html'}
    }
    manifest: dict[str, object] = {
        'pyodide': 'https://cdn.jsdelivr.net/pyodide/v314.0.6/full/pyodide.mjs',
        'wheels': staged,
        'sources': sources,
        'versions': {
            **{wheel['name']: wheel['version'] for wheel in wheels},
            'django-tags-input': importlib.metadata.version(
                'django-tags-input'
            ),
        },
    }
    (destination / 'manifest.json').write_text(json.dumps(manifest))
    for filename in (
        'jquery-3.2.1.min.js',
        'jquery-ui-1.12.1.min.js',
        'jquery-ui-1.12.1.min.css',
        'jquery.tagsinput-revisited-2.0.min.js',
        'jquery.tagsinput-revisited-2.0.min.css',
    ):
        shutil.copy2(ROOT / 'tags_input/static' / filename, destination)
    shutil.copytree(
        ROOT / 'tags_input/static/images',
        destination / 'images',
        dirs_exist_ok=True,
    )
    shutil.copytree(
        ROOT / 'tags_input/static/licences',
        destination / 'licences',
        dirs_exist_ok=True,
    )
    for filename in ('index.html', 'playground.css'):
        shutil.copy2(ROOT / 'playground' / filename, destination)


def main() -> None:
    """Build static assets only, or assets followed by warning-free Sphinx."""
    if sys.version_info < (3, 11):
        raise RuntimeError('Building the documentation requires Python 3.11+')
    parser: argparse.ArgumentParser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--assets-only', action='store_true')
    parser.add_argument(
        '--output', type=Path, default=ROOT / 'docs/_build/html'
    )
    args: argparse.Namespace = parser.parse_args()
    stage(ROOT / 'docs/_static/playground')
    if not args.assets_only:
        run(
            sys.executable,
            '-m',
            'sphinx',
            '-W',
            '-b',
            'html',
            'docs',
            str(args.output),
        )


if __name__ == '__main__':
    main()
