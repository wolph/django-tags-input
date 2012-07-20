from django.conf import settings
from django.db import models
from . import exceptions

def get_mappings():
    '''
    Get all mappings from the settings
    
    To use the Django Tags Input module the `TAGS_INPUT_SETTINGS` must be
    defined.
    '''
    return getattr(settings, 'TAGS_INPUT_MAPPINGS', {})

def get_mapping(model_or_queryset):
    '''Get the mapping for a given model or queryset'''
    mappings = get_mappings()

    if isinstance(model_or_queryset, models.query.QuerySet):
        queryset = model_or_queryset
        model = model_or_queryset.model
    elif issubclass(model_or_queryset, models.Model):
        queryset = model_or_queryset.objects.all()
        model = model_or_queryset
    else:
        raise TypeError('Only `django.db.model.Model` and '
            '`django.db.query.QuerySet` objects are valid arguments')

    meta = model._meta
    mapping_key = meta.app_label + '.' + meta.object_name

    mapping = mappings.get(mapping_key)
    if mapping:
        mapping = mapping.copy()
    else:
        raise exceptions.MappingUndefined('Unable to find mapping '
            'for %s' % mapping_key)

    mapping['app'] = meta.app_label
    mapping['model'] = meta.object_name
    mapping['queryset'] = queryset

    return mapping.copy()

