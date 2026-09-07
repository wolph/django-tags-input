"""Configuration file for the Sphinx documentation builder."""

from __future__ import annotations

from datetime import date

import django
from django.conf import settings

from tags_input import __about__

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'tags_input',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
    )
    django.setup()

project = 'Django Tags Input'
author = __about__.__author__
copyright = f'{date.today().year}, {author}'  # noqa: A001

release = __about__.__version__
version = '.'.join(release.split('.')[:2])

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'myst_parser',
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False

autodoc_typehints = 'description'
autodoc_member_order = 'bysource'

myst_enable_extensions = ['colon_fence']
myst_heading_anchors = 3

templates_path = ['_templates']
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    'superpowers',
    'superpowers/**',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': (
        'https://docs.djangoproject.com/en/stable/',
        'https://docs.djangoproject.com/en/stable/_objects/',
    ),
}

html_theme = 'furo'
html_static_path = ['_static']
html_title = f'{project} {release}'
html_theme_options = {
    'source_repository': 'https://github.com/WoLpH/django-tags-input/',
    'source_branch': 'develop',
    'source_directory': 'docs/',
}
