"""
Metadata about the `django-tags-input` package.

Attributes:
    __package_name__ (str): The distribution name as published on PyPI.
    __author__ (str): The author of the package.
    __author_email__ (str): The email of the author.
    __description__ (str): A brief description of the package.
    __url__ (str): The URL of the package's repository.
    __version__ (str): The current version, read from the installed metadata.
"""

from __future__ import annotations

from importlib import metadata

#: Distribution name as published on PyPI.
__package_name__: str = 'django-tags-input'
#: Primary author's name.
__author__: str = 'Rick van Hattem'
#: Primary author's contact email.
__author_email__: str = 'wolph@wol.ph'
#: One-line description of the package.
__description__: str = (
    'Django form field, widget and admin mixin that turn ManyToMany '
    'relations into ordered, autocompleting tag inputs with optional '
    'on-the-fly creation.'
)
#: Canonical project/repository URL.
__url__: str = 'https://github.com/WoLpH/django-tags-input'

try:
    # `[project].version` in pyproject.toml is the single source of truth.
    # Read it back at runtime so the two never drift.
    __version__: str = metadata.version(__package_name__)
except metadata.PackageNotFoundError:  # pragma: no cover
    # Not installed (e.g. running straight from a source checkout).
    __version__ = '0.0.0'

__all__: list[str] = [
    '__author__',
    '__author_email__',
    '__description__',
    '__package_name__',
    '__url__',
    '__version__',
]
