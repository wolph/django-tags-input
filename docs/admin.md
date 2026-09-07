# Admin integration

The admin integration is the main reason this package exists. Subclass
{class}`~tags_input.admin.TagsInputAdmin` instead of `admin.ModelAdmin` and
every `ManyToManyField` on the model renders as a tags input:

```python
from django.contrib import admin

from tags_input import admin as tags_input_admin

from . import models


@admin.register(models.Post)
class PostAdmin(tags_input_admin.TagsInputAdmin):
    list_display = ('title', 'published')
```

```{image} _static/admin-autocomplete.png
:alt: The admin change form for a model with a tags input and an open autocomplete list
:width: 100%
```

## Choosing which fields become tags

Set `tag_fields` to limit the conversion to some of the `ManyToManyField`s.
Fields that are not listed keep Django's default widget:

```python
@admin.register(models.Post)
class PostAdmin(tags_input_admin.TagsInputAdmin):
    tag_fields = ('tags',)
```

For a dynamic decision, override `get_tag_fields()` and return the field
names. Returning `None` converts every field.

Fields with a custom `through` model are left alone, exactly as Django's own
admin leaves them out of the form. Only auto-created through tables can be
managed by the widget.

## Inlines

{class}`~tags_input.admin.TagsInputTabularInline` and
{class}`~tags_input.admin.TagsInputStackedInline` do the same for inline
forms. Combine them with a `TagsInputAdmin` parent, or with a plain
`ModelAdmin` if only the inline needs tags:

```python
class SectionInline(tags_input_admin.TagsInputStackedInline):
    model = models.Section
    tag_fields = ('keywords',)


@admin.register(models.Post)
class PostAdmin(tags_input_admin.TagsInputAdmin):
    inlines = (SectionInline,)
```

```{image} _static/admin-inline.png
:alt: A stacked inline in the admin with tags inputs on each inline form
:width: 100%
```

## The form mixin

`TagsInputAdmin.get_form()` and the inline `get_formset()` wrap the generated
form class in {class}`~tags_input.admin.TagsInputFormMixin`. The mixin does
two things:

- On load, it sets the initial value of every `TagsInputField` from the
  through table, ordered by the through row's primary key, so the widget
  shows the tags in the order they were saved.
- On save, after Django's own `_save_m2m()`, it clears the relation and adds
  the objects back in the order the user typed them.

You can use the mixin on your own `ModelForm` as well, which is what makes
the order round-trip in views outside the admin. See {doc}`forms`.

## Notes and caveats

The mixin clears the relation, then calls `add()` once for each object.
Django emits `pre_clear` and `post_clear`, followed by `pre_add` and
`post_add` for each object. Django's earlier `_save_m2m()` can emit additional
signals. Signal handlers must allow for this sequence.

`TagsInputMixin.formfield_for_manytomany()` appends the field name to
`raw_id_fields` to stop the admin from adding the green plus icon next to the
widget. It is a documented hack, and it means `raw_id_fields` on your admin
class grows at runtime.
