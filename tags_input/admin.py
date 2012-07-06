from django.contrib import admin
from . import fields


class TagsInputAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        '''
        Get a form Field for a ManyToManyField.
        '''
        # If it uses an intermediary model that isn't auto created, don't show
        # a field in admin.
        if not db_field.rel.through._meta.auto_created:
            return None

        queryset = db_field.rel.to._default_manager.get_query_set()

        db = kwargs.get('using')
        if db:
            queryset = queryset.using(db)
        kwargs['queryset'] = queryset
        kwargs['widget'] = fields.AdminTagsInputField.widget(
            db_field.verbose_name,
            (db_field.name in self.filter_vertical),
        )
        kwargs['required'] = not db_field.blank
        return fields.AdminTagsInputField(**kwargs)


