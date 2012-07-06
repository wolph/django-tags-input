from django.conf import settings
from django import forms
from . import widgets
from . import exceptions
from django.core.exceptions import ValidationError

class TagsInputField(forms.ModelMultipleChoiceField):
    widget = widgets.TagsInputWidget

    def __init__(self, queryset, **kwargs):
        super(TagsInputField, self).__init__(queryset, **kwargs)
        self.create_missing = kwargs.pop('create_missing', False)
        self.mapping = kwargs.pop('mapping', None)
        self.widget.mapping = self.get_mapping()

    def get_mapping(self):
        if not self.mapping:
            mappings = getattr(settings, 'TAGS_INPUT_MAPPINGS', {})
            meta = self.queryset.model._meta
            mapping_key = meta.app_label + '.' + meta.object_name
            mapping = mappings.get(mapping_key).copy()
            if not mapping:
                raise exceptions.MappingUndefined('Unable to find mapping '
                    'for %s' % mapping_key)

            self.mapping = mapping
            mapping['app'] = meta.app_label
            mapping['model'] = meta.object_name
            mapping['queryset'] = self.queryset
            mapping['create_missing'] = (self.create_missing or 
                mapping.get('create_missing', False))

        return self.mapping

    def clean(self, value):
        mapping = self.get_mapping()
        field = mapping['field']
        values = dict(self.queryset
            .filter(**{'%s__in' % field: value})
            .values_list(field, 'pk')
        )
        missing = set(value) - set(values)
        if missing:
            if mapping['create_missing']:
                for v in missing:
                    o = self.queryset.model(**{
                        field: v,
                    })
                    if hasattr(o, 'clean'):
                        o.clean()
                    elif hasattr(o, 'full_clean'):
                        o.full_clean()
                    o.save()
                    values[v] = o.pk
            else:
                raise ValidationError(self.error_messages['invalid_choice']
                    % ', '.join(missing))

        ids = []
        for v in value:
            ids.append(values[v])

        return forms.ModelMultipleChoiceField.clean(self, ids)

class AdminTagsInputField(TagsInputField):
    widget = widgets.AdminTagsInputWidget

