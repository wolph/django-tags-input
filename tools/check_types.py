"""Run checkers against the active environment and explicit project files."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[1]


def main() -> None:
    """Avoid accidentally checking a different virtual environment's stubs."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(__doc__)
    parser.add_argument('checker', choices=('mypy', 'pyright', 'pyrefly'))
    parser.add_argument('--python-version')
    args: argparse.Namespace = parser.parse_args()
    command: list[str]
    version_flag: str = '--python-version'
    if args.checker == 'mypy':
        command = ['mypy', '--python-executable', sys.executable]
    elif args.checker == 'pyright':
        command = ['basedpyright', '--pythonpath', sys.executable]
        version_flag = '--pythonversion'
    else:
        command = [
            'pyrefly',
            'check',
            '--python-interpreter-path',
            sys.executable,
            '--use-ignore-files=false',
        ]
        # Explicit files also work in locally ignored Git worktrees.
        command.extend(
            str(path.relative_to(ROOT))
            for directory in ('tags_input', 'example', 'showcase')
            for path in sorted((ROOT / directory).rglob('*.py'))
            if 'migrations' not in path.parts
        )
    if args.python_version:
        command.extend([version_flag, args.python_version])
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
