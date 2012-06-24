from django.db import models
from django import http
from django.utils import simplejson

def autocomplete(request, app, model, field):
    queryset = (models
        .get_model(app, model)
        .objects.all()
        .values_list(field, flat=True)
        .order_by(field)
    )

    term = request.GET.get('term')
    if term:
        queryset = queryset.filter(**{'%s__istartswith' % field: term})

    max_results = request.GET.get('max_results')
    if max_results and max_results.isdigit():
        max_results = int(max_results)
    else:
        max_results = 10

    results = list(queryset[:max_results])
    if results:
        response = simplejson.dumps(results),
    else:
        response = ''

    return http.HttpResponse(response, mimetype='application/javascript')

