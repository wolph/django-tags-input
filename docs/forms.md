# Forms outside the admin

Try creation, strict selection and composite labels in the {doc}`playground`.

{class}`~tags_input.fields.TagsInputField` is a
`ModelMultipleChoiceField` with a different widget and a smarter `clean()`.
It works in any form:

```python
from django import forms

from tags_input import fields

from . import models


class PostForm(forms.ModelForm):
    tags = fields.TagsInputField(
        models.Tag.objects.all(),
        create_missing=True,
        required=False,
    )

    class Meta:
        model = models.Post
        fields = ['title', 'tags']
```

The first argument is the queryset the tags come from. Its model must have an
entry in `TAGS_INPUT_MAPPINGS`, otherwise the field raises
{class}`~tags_input.exceptions.MappingUndefined` when it is constructed.

`create_missing=True` on the field enables creation even when the mapping
defaults to strict matching. Setting it to `False` does not disable creation
when the mapping enables it. Keep creation disabled in the mapping if only
some forms should allow it.

## Rendering

The widget needs its JavaScript and CSS on the page. Render the form's media
in the `<head>` and the form wherever you want it:

```django
{{ form.media }}
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
</form>
```

```{image} _static/form-demo.png
:alt: A plain Django form rendering a tags input with autocomplete suggestions
:width: 100%
```

With `TAGS_INPUT_INCLUDE_JQUERY = True` (the default) the media includes
jQuery 3.2 and jQuery UI 1.12. If your page already loads jQuery and jQuery
UI, set it to `False` and only the tagsinput plugin is included.

## Keeping the order in your own views

`clean()` returns the objects in typed order, but a plain `ModelForm.save()`
hands the queryset to `field.set()`, which does not promise any order. Mix in
{class}`~tags_input.admin.TagsInputFormMixin` to get the same re-link the
admin does:

```python
from tags_input import admin as tags_input_admin


class PostForm(tags_input_admin.TagsInputFormMixin, forms.ModelForm):
    tags = fields.TagsInputField(models.Tag.objects.all(), required=False)

    class Meta:
        model = models.Post
        fields = ['title', 'tags']
```

The mixin only acts on `TagsInputField`s whose relation uses an auto-created
through table. Other fields are untouched.

## JavaScript hooks

{class}`~tags_input.widgets.TagsInputWidget` and
{class}`~tags_input.widgets.AdminTagsInputWidget` accept `on_add_tag`,
`on_remove_tag` and `on_change_tag` as keyword arguments. Each is a
JavaScript expression that is inserted verbatim as the plugin callback:

```python
from tags_input import fields, widgets

tags = fields.TagsInputField(
    models.Tag.objects.all(),
    widget=widgets.TagsInputWidget(
        on_add_tag='function (tag) { console.log("added", tag); }',
    ),
)
```

The expressions are rendered into an inline `<script>` block without
escaping, so never build them from user input.

## What the widget posts

The rendered input is a single text field holding the labels separated by
commas. The plugin also keeps a hidden `<name>_incomplete` field with any
text the user typed but did not confirm, and the widget appends that to the
submitted tags so a half-typed label is not silently dropped. Both are
handled by `value_from_datadict()`, so your view only ever sees the cleaned
list of labels.

## Try a saved selection

Add a tag and save it here. The same browser database is available on the
[dedicated example page](playground.md).

```{raw} html
<iframe src="_static/playground/index.html" title="Try saving ordered Django tags" style="width:100%;height:950px;border:0;border-radius:12px" loading="lazy"></iframe>
```
