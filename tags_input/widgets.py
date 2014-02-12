from django.conf import settings
from django import forms
from django.template.loader import render_to_string
from django.core import urlresolvers
from django.contrib.admin import widgets
from django.utils import datastructures


class TagsInputWidgetBase(forms.SelectMultiple):
    def __init__(self, on_add_tag=None, on_remove_tag=None, on_change_tag=None,
                 *args, **kwargs):
        self.on_add_tag = on_add_tag
        self.on_remove_tag = on_remove_tag
        self.on_change_tag = on_change_tag
        forms.SelectMultiple.__init__(self, *args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        context = self.build_attrs(attrs, name=name)
        context['on_add_tag'] = self.on_add_tag
        context['on_remove_tag'] = self.on_remove_tag
        context['on_change_tag'] = self.on_change_tag

        context['STATIC_URL'] = settings.STATIC_URL
        context['mapping'] = self.mapping
        context['autocomplete_url'] = urlresolvers.reverse(
            'tags_input:autocomplete',
            kwargs=dict(
                app=self.mapping['app'],
                model=self.mapping['model'],
                fields='-'.join(self.mapping['fields']),
            ),
        )

        if value:
            fields = self.mapping['fields']
            join_func = self.mapping['join_func']

            ids = []
            for v in value:
                if isinstance(v, (int, long)):
                    ids.append(v)

            values_map = datastructures.SortedDict(map(
                join_func,
                self.mapping['queryset']
                .filter(pk__in=ids)
                .values('pk', *fields)
                .order_by('pk')
            ))

            values = []
            for v in value:
                if isinstance(v, (int, long)):
                    values.append(values_map[v])
                else:
                    values.append(v)

            context['values'] = ', '.join(values)

        return render_to_string('tags_input_widget.html', context)

    def value_from_datadict(self, data, files, name):
        tags = data.get(name, '').split(',')
        incomplete = data.get(name + '_incomplete', '')
        if incomplete != data.get(name + '_default'):
            tags += incomplete.split(',')
        return [t.strip() for t in tags if t]


class TagsInputWidget(TagsInputWidgetBase):
    class Media:
        css = {
            'all': (
                'css/jquery.tagsinput.css',
            ),
        }
        js = (
            'js/jquery.tagsinput.js',
        )
        enable_jquery = getattr(settings, 'TAGS_INPUT_INCLUDE_JQUERY', True)
        if enable_jquery:  # pragma: no cover
            css['all'] += 'css/base/jquery.ui.all.css',
            js += (
                'js/jquery-1.7.2.min.js',
                'js/jquery-ui-18.1.16.min.js',
            )


class AdminTagsInputWidget(widgets.FilteredSelectMultiple,
                           TagsInputWidgetBase):
    class Media:
        css = getattr(settings, 'TAGS_INPUT_ADMIN_CSS', {
            'all': (
                'css/jquery.tagsinput.css',
                'css/base/jquery.ui.all.css',
            ),
        })
        js = getattr(settings, 'TAGS_INPUT_ADMIN_JS', (
            'js/jquery-1.7.2.min.js',
            'js/jquery-ui-18.1.16.min.js',
            'js/jquery.tagsinput.js',
        ))

