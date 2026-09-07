"""Views for handling tags input autocompletion requests."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING

from django import http
from django.apps import apps
from django.db import models

from . import utils
from .types import TagMapping

if TYPE_CHECKING:
    from .types import ValueQuerySet


def get_model(app: str, model: str) -> type[models.Model]:
    """Retrieve a Django model class given app label and model name."""
    return apps.get_model(app, model)


def _filter_func(
    queryset: ValueQuerySet, field: str, term: str
) -> ValueQuerySet:
    return queryset.filter(**{f'{field}__istartswith': term})


def autocomplete(
    request: http.HttpRequest, app: str, model: str, fields: str
) -> http.HttpResponse:
    """Handle autocompletion queries and return matching tags as JSON."""
    model_cls: type[models.Model] = get_model(app, model)
    mapping: TagMapping = utils.get_mapping(model_cls)
    field_list: list[str] = fields.split('-')

    raw_queryset: ValueQuerySet = (
        mapping['queryset']
        .filter(**mapping.get('filters', {}))
        .exclude(**mapping.get('excludes', {}))
        .values('pk', *field_list)
        .order_by(*mapping.get('ordering', field_list))
    )
    autocomplete_filter: Callable[[ValueQuerySet, str, str], ValueQuerySet] = (
        mapping.get('autocomplete_queryset_filter', _filter_func)
    )
    term: str | None = request.GET.get('term')
    queryset: ValueQuerySet
    if term:
        queryset = raw_queryset.none()
        for field in field_list:
            queryset = queryset | autocomplete_filter(
                raw_queryset, field, term
            )
    else:
        queryset = raw_queryset

    max_results_raw: str | None = request.GET.get('max_results')
    max_results: int = (
        int(max_results_raw)
        if max_results_raw and max_results_raw.isdigit()
        else 10
    )

    results: list[str] = [
        mapping['join_func'](v)[1] for v in queryset[:max_results]
    ]
    response: str = json.dumps(results) if results else ''

    return http.HttpResponse(response, content_type='application/javascript')


__all__: list[str] = ['autocomplete', 'get_model']
