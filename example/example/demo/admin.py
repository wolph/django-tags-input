# vim: set fileencoding=utf-8 :
from django.contrib import admin
from tags_input import admin as tags_input_admin

from . import models


class InlineModelInline(tags_input_admin.TagsInputStackedInline):
    model = models.InlineModel


class SimpleNameAdmin(tags_input_admin.TagsInputAdmin):

    inlines = [
        InlineModelInline,
    ]
    list_display = ('id', 'name')
    search_fields = ('name',)


class DoubleNameAdmin(tags_input_admin.TagsInputAdmin):

    list_display = ('id', 'name_a', 'name_b')


class ErrorNameAdmin(tags_input_admin.TagsInputAdmin):

    list_display = ('id', 'name')
    search_fields = ('name',)


class ForeignKeyToSimpleNameAdmin(tags_input_admin.TagsInputAdmin):

    list_display = ('id', 'name', 'simple_name')
    list_filter = ('simple_name',)
    search_fields = ('name',)


class ManyToManyToSimpleNameAdmin(tags_input_admin.TagsInputAdmin):

    list_display = ('id', 'name')
    raw_id_fields = ('simple_names',)
    search_fields = ('name',)


class ManyToManyToDoubleNameAdmin(tags_input_admin.TagsInputAdmin):

    list_display = ('id', 'name')
    raw_id_fields = ('double_names',)
    search_fields = ('name',)


class ManyToManyToErrorAdmin(tags_input_admin.TagsInputAdmin):

    list_display = ('id', 'name')
    raw_id_fields = ('simple_names',)
    search_fields = ('name',)


class ThroughModelAdmin(tags_input_admin.TagsInputAdmin):

    list_display = ('id', 'name', 'simple_name', 'many_to_many_through')
    list_filter = ('simple_name', 'many_to_many_through')
    search_fields = ('name',)


class ManyToManyThroughAdmin(tags_input_admin.TagsInputAdmin):

    list_display = ('id', 'name')
    raw_id_fields = ('simple_names',)
    search_fields = ('name',)


class InlineModelAdmin(tags_input_admin.TagsInputAdmin):

    list_display = ('id', 'name')
    raw_id_fields = ('simple_names',)
    search_fields = ('name',)
    tag_fields = {'simple_names', }


def _register(model, admin_class):
    admin.site.register(model, admin_class)


_register(models.SimpleName, SimpleNameAdmin)
_register(models.DoubleName, DoubleNameAdmin)
_register(models.ErrorName, ErrorNameAdmin)
_register(models.ForeignKeyToSimpleName, ForeignKeyToSimpleNameAdmin)
_register(models.ManyToManyToSimpleName, ManyToManyToSimpleNameAdmin)
_register(models.ManyToManyToDoubleName, ManyToManyToDoubleNameAdmin)
_register(models.ManyToManyToError, ManyToManyToErrorAdmin)
_register(models.ThroughModel, ThroughModelAdmin)
_register(models.ManyToManyThrough, ManyToManyThroughAdmin)
_register(models.InlineModel, InlineModelAdmin)
