from django.contrib import admin
import fields
import widgets


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

        kwargs['queryset'] = queryset
        kwargs['widget'] = widgets.AdminTagsInputWidget(
            db_field.verbose_name,
            (db_field.name in self.filter_vertical),
        )
        kwargs['required'] = not db_field.blank

        # Ugly hack to stop the Django admin from adding the + icon
        if db_field.name not in self.raw_id_fields:
            self.raw_id_fields = list(self.raw_id_fields)
            self.raw_id_fields.append(db_field.name)

        return fields.AdminTagsInputField(**kwargs)

