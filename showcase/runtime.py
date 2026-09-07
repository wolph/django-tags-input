"""A JSON boundary around real Django forms, storage and autocomplete."""

from __future__ import annotations

import json
import os
from typing import Any, cast


def initialise(database_path: object) -> None:
    """Configure standalone Django and create only missing showcase tables."""
    if (
        not isinstance(database_path, str)
        or not database_path
        or '\x00' in database_path
    ):
        raise ValueError('Invalid database path')
    from django.conf import settings

    if not settings.configured:
        os.environ['SHOWCASE_DATABASE'] = database_path
        os.environ['DJANGO_SETTINGS_MODULE'] = 'showcase.settings'
    import django

    django.setup()
    from django.db import connection

    from .models import Article, Contact, Tag
    from .seed import seed

    tables: list[str] = connection.introspection.table_names()
    with connection.schema_editor() as editor:
        for model in (Tag, Contact, Article):
            if model._meta.db_table not in tables:
                editor.create_model(model)
    seed()


def validate(payload: object) -> dict[str, str]:
    """Reject unsupported messages before reaching the database."""
    if not isinstance(payload, str) or len(payload) > 16384:
        raise ValueError('Invalid request size')
    try:
        data: object = json.loads(payload)
    except (ValueError, RecursionError) as exc:
        raise ValueError('Invalid JSON') from exc
    if not isinstance(data, dict):
        raise ValueError('Expected an object')  # noqa: TRY004 - JSON contract
    request: dict[str, object] = cast(dict[str, object], data)
    if set(request) - {'action', 'mode', 'values', 'term'}:
        raise ValueError('Unknown request field')
    if not all(isinstance(value, str) for value in request.values()):
        raise ValueError('Request fields must be strings')
    parsed: dict[str, str] = cast(dict[str, str], request)
    if parsed.get('action') not in (
        'load',
        'save',
        'suggest',
        'reset',
    ) or parsed.get('mode') not in ('create', 'existing', 'composite'):
        raise ValueError('Invalid action or mode')
    if (
        len(parsed.get('values', '')) > 4096
        or len(parsed.get('term', '')) > 100
    ):
        raise ValueError('Input is too long')
    if any(
        len(value.strip()) > 100
        for value in parsed.get('values', '').split(',')
    ):
        raise ValueError('Tag is too long')
    return parsed


def dispatch_json(payload: str) -> str:
    """Dispatch a validated request without evaluating supplied code."""
    request: dict[str, str] = validate(payload)
    from .seed import seed

    mode: str = request['mode']
    action: str = request['action']
    seed(reset=action == 'reset')
    if action == 'suggest':
        return suggest(mode, request.get('term', ''))
    return json.dumps(
        form_state(
            mode, request.get('values', '') if action == 'save' else None
        )
    )


def suggest(mode: str, term: str) -> str:
    """Call the installed package autocomplete view through its URL."""
    from django.test import RequestFactory
    from django.urls import resolve, reverse

    model: str = 'Contact' if mode == 'composite' else 'Tag'
    fields: str = 'first_name-last_name' if mode == 'composite' else 'name'
    path: str = reverse(
        'tags_input:autocomplete',
        kwargs={'app': 'showcase', 'model': model, 'fields': fields},
    )
    match = resolve(path)
    response = match.func(
        RequestFactory().get(path, {'term': term}), **match.kwargs
    )
    return response.content.decode() or '[]'


def form_state(mode: str, values: str | None = None) -> dict[str, Any]:
    """Render a bound field and report submitted and stored selections."""
    from django.db import DatabaseError, transaction

    from tags_input.utils import get_tags

    from .forms import FORMS
    from .models import Article

    if values is not None:
        values = ','.join(
            value.strip() for value in values.split(',') if value.strip()
        )
    article: Article = Article.objects.get(title=mode)
    field_name: str = 'contacts' if mode == 'composite' else 'tags'
    form = FORMS[mode](
        None if values is None else {field_name: values}, instance=article
    )
    if values is not None:
        try:
            with transaction.atomic():
                if form.is_valid():
                    form.save()
                else:
                    transaction.set_rollback(True)
        except DatabaseError:
            form.add_error(
                field_name,
                'Unable to save this selection. Check for duplicate new tags.',
            )
    stored: list[str] = [
        str(tag)
        for tag in get_tags(Article.objects.get(pk=article.pk), field_name)
    ]
    selected: list[str] = (
        stored
        if values is None
        else [value.strip() for value in values.split(',') if value.strip()]
    )
    return {
        'mode': mode,
        'field_html': str(form[field_name]),
        'field_name': field_name,
        'selected': selected,
        'stored': stored,
        'errors': {
            name: [str(error) for error in errors]
            for name, errors in form.errors.items()
        },
    }
