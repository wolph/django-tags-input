"""Views for handling tags input autocompletion requests."""

import json
from collections.abc import Callable, Iterable, Mapping
from typing import Any, cast

from django import http
from django.apps import apps
from django.db import models

from . import utils


def get_model(app: str, model: str) -> type[models.Model]:
    """Retrieve a Django model class given app label and model name."""
    return apps.get_model(app, model)


def _filter_func(
    queryset: models.QuerySet[Any], field: str, term: str
) -> models.QuerySet[Any]:
    qs: Any = queryset
    return cast(
        models.QuerySet[Any],
        qs.filter(**{f'{field}__istartswith': term}),
    )


def autocomplete(
    request: http.HttpRequest, app: str, model: str, fields: str
) -> http.HttpResponse:
    """Handle autocompletion queries and return matching tags as JSON."""
    model_cls: type[models.Model] = get_model(app, model)
    mapping: dict[str, Any] = utils.get_mapping(model_cls)
    field_list: list[str] = fields.split('-')

    raw_queryset: models.QuerySet[Any] = cast(
        models.QuerySet[Any],
        mapping['queryset']
        .filter(**mapping.get('filters', {}))
        .exclude(**mapping.get('excludes', {}))
        .values('pk', *field_list)
        .order_by(*mapping.get('ordering', field_list)),
    )
    autocomplete_filter: Callable[
        [models.QuerySet[Any], str, str], models.QuerySet[Any]
    ] = mapping.get('autocomplete_queryset_filter', _filter_func)
    term: str | None = request.GET.get('term')
    queryset: models.QuerySet[Any]
    if term:
        empty_qs: Any = mapping['queryset'].none()
        queryset = cast(models.QuerySet[Any], empty_qs)
        for field in field_list:
            filtered: Any = autocomplete_filter(raw_queryset, field, term)
            combined: Any = cast(Any, queryset) | filtered
            queryset = cast(models.QuerySet[Any], combined)
    else:
        queryset = raw_queryset

    max_results_raw: str | None = request.GET.get('max_results')
    max_results: int = (
        int(max_results_raw)
        if max_results_raw and max_results_raw.isdigit()
        else 10
    )

    results: list[str] = [
        str(mapping['join_func'](v)[1])
        for v in cast(Iterable[Mapping[str, Any]], queryset[:max_results])
    ]
    response: str = json.dumps(results) if results else ''

    return http.HttpResponse(response, content_type='application/javascript')


__all__: list[str] = ['autocomplete', 'get_model']
