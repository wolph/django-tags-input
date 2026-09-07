"""Standalone settings for the isolated showcase database."""

from __future__ import annotations

import os
from pathlib import Path

from tags_input.types import MappingOptions

BASE_DIR: Path = Path(__file__).resolve().parent
SECRET_KEY: str = 'local-showcase-only-not-for-deployment'
DEBUG: bool = True
ALLOWED_HOSTS: list[str] = ['localhost', '127.0.0.1', 'testserver']
INSTALLED_APPS: list[str] = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tags_input',
    'showcase',
]
MIDDLEWARE: list[str] = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF: str = 'showcase.urls'
DATABASES: dict[str, dict[str, str]] = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get(
            'SHOWCASE_DATABASE', str(BASE_DIR / 'showcase.sqlite3')
        ),
    }
}
TEMPLATES: list[dict[str, object]] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        },
    }
]
DEFAULT_AUTO_FIELD: str = 'django.db.models.AutoField'
STATIC_URL: str = '/static/'
USE_TZ: bool = True
TAGS_INPUT_INCLUDE_JQUERY: bool = True
TAGS_INPUT_MAPPINGS: dict[str, MappingOptions] = {
    'showcase.Tag': {'field': 'name', 'create_missing': False},
    'showcase.Contact': {'fields': ('first_name', 'last_name')},
}
