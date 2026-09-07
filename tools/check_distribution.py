"""Check installed wheel assets outside the source checkout."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[1]
SMOKE: str = r"""
import re
from pathlib import Path
import tags_input
root = Path(tags_input.__file__).parent
assert 'site-packages' in root.parts, root
assert (root / 'py.typed').is_file()
static = root / 'static'
references = []
for css in static.glob('*.css'):
    pattern = r'url\(["\x27]?([^\)"\x27]+)'
    for reference in re.findall(pattern, css.read_text()):
        if not reference.startswith('data:'):
            references.append(reference)
            assert (css.parent / reference).is_file(), reference
assert len(set(references)) >= 6, references
for name in ('jquery.txt', 'jquery-ui.txt', 'tagsinput-revisited.txt'):
    assert (static / 'licences' / name).is_file(), name
assert not (static / 'jquery-ui-1.12.1').exists()
assert not (static / 'jquery-tagsinput-revisited-2.0').exists()
assert (root / 'templates/tags_input_widget.html').is_file()
print('Installed wheel assets and typed marker verified')
"""


def main() -> None:
    """Build and install the wheel outside the checkout."""
    with tempfile.TemporaryDirectory(prefix='tags-input-wheel-') as temporary:
        directory: Path = Path(temporary)
        subprocess.run(
            ['uv', 'build', '--out-dir', str(directory / 'dist')],
            cwd=ROOT,
            check=True,
        )
        wheel: Path = next((directory / 'dist').glob('*.whl'))
        environment: Path = directory / 'venv'
        subprocess.run(['uv', 'venv', str(environment)], check=True)
        python: Path = environment / 'bin/python'
        subprocess.run(
            ['uv', 'pip', 'install', '--python', str(python), str(wheel)],
            check=True,
        )
        subprocess.run([str(python), '-c', SMOKE], cwd=directory, check=True)


if __name__ == '__main__':
    main()
