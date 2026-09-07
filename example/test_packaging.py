"""Check that distributed widget assets are self-contained."""

from __future__ import annotations

import re
from pathlib import Path


def test_widget_css_images_exist() -> None:
    static: Path = Path(__file__).parents[1] / 'tags_input' / 'static'
    css: str = (static / 'jquery-ui-1.12.1.min.css').read_text()
    references: set[str] = set(re.findall(r'url\(["\']?([^\)"\']+)', css))
    missing: list[str] = [
        reference
        for reference in references
        if not reference.startswith('data:')
        and not (static / reference).is_file()
    ]
    assert missing == [], f'Missing stylesheet assets: {missing}'


def test_widget_third_party_notices_exist() -> None:
    notices: Path = (
        Path(__file__).parents[1] / 'tags_input' / 'static' / 'licences'
    )
    for filename in ('jquery.txt', 'jquery-ui.txt', 'tagsinput-revisited.txt'):
        assert (notices / filename).is_file(), filename
