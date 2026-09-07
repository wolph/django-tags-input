"""Keep submitted showcase labels distinct from model primary keys."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, cast

from django.utils.safestring import SafeString

from tags_input.widgets import TagsInputWidget


@dataclass(frozen=True)
class _Label:
    """Carry a literal label through the package widget's ID conversion."""

    value: str

    def __str__(self) -> str:
        """Return the unchanged label for normal template escaping."""
        return self.value


class ShowcaseWidget(TagsInputWidget):
    """Treat posted strings as labels and retain integer initial IDs."""

    def render(
        self,
        name: str,
        value: Any,
        attrs: dict[str, Any] | None = None,
        renderer: Any = None,
    ) -> SafeString:
        """Render literal submitted labels with the real package widget."""
        values: Sequence[object] = cast(Sequence[object], value or ())
        labels: list[object] = [
            _Label(item) if isinstance(item, str) else item for item in values
        ]
        return super().render(name, labels, attrs, renderer)
