from django.contrib import admin
import models
from tags_input import admin as tags_input_admin

class FooAdmin(tags_input_admin.TagsInputAdmin):
    list_display = (
        'pk',
        'name',
    )
    search_fields = ('name',)


class BarAdmin(tags_input_admin.TagsInputAdmin):
    list_display = (
        'pk',
        'name',
        'foo',
    )
    search_fields = ('name',)


class SpamAdmin(tags_input_admin.TagsInputAdmin):
    list_display = (
        'pk',
        'name',
    )
    search_fields = ('name',)


class ExtraSpamAdmin(tags_input_admin.TagsInputAdmin):
    list_display = (
        'pk',
        'name',
    )
    search_fields = ('name',)


class EggAdmin(tags_input_admin.TagsInputAdmin):
    list_display = (
        'pk',
        'name',
        'foo',
    )
    search_fields = ('name',)

admin.site.register(models.Foo, FooAdmin)
admin.site.register(models.Bar, BarAdmin)
admin.site.register(models.Spam, SpamAdmin)
admin.site.register(models.ExtraSpam, ExtraSpamAdmin)
admin.site.register(models.Egg, EggAdmin)

