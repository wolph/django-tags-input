from django.db import models
from django import http
from django.utils import simplejson

from . import utils


def _filter_func(queryset, field, term):
    return queryset.filter(**{'%s__istartswith' % field: term})


def autocomplete(request, app, model, fields):
    model = models.get_model(app, model)
    mapping = utils.get_mapping(model)
    fields = fields.split('-')

    raw_queryset = (
        mapping['queryset']
        .filter(**mapping.get('filters', {}))
        .exclude(**mapping.get('excludes', {}))
        .values('pk', *fields)
        .order_by(*mapping.get('ordering', fields))
    )
    autocomplete_filter = mapping.get('autocomplete_queryset_filter',
                                      _filter_func)
    term = request.GET.get('term')
    if term:
        queryset = mapping['queryset'].none()
        for field in fields:
            queryset |= autocomplete_filter(raw_queryset, field, term)
    else:
        queryset = raw_queryset

    max_results = request.GET.get('max_results')
    if max_results and max_results.isdigit():
        max_results = int(max_results)
    else:
        max_results = 10

    results = [mapping['join_func'](v)[1] for v in queryset[:max_results]]
    if results:
        response = simplejson.dumps(results),
    else:
        response = ''

    return http.HttpResponse(response, mimetype='application/javascript')

