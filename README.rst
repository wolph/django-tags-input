Overview
--------

Django Tags Input is a module that gives you a modified version of the `Xoxco jQuery Tags Input`_ library within Django.

The result is a very pretty interface with tags and autocomplete which can optionally automatically create new items when they are missing.

.. _Xoxco jQuery Tags Input: http://xoxco.com/projects/code/tagsinput/

One of the most useful features of Django Tags Input is that it stores the elements in the order which you input.

So if you insert `B, A, C` into the database, it will return it sorted the way you entered it: `B, A, C`.

How to install
--------------

Installing this module only takes a couple of minutes.

1. Install the module itself

    pip install django-tags-input

    # or
    
    easy_install django-tags-input

2. Add ``tags_input`` to your ``INSTALLED_APPS`` setting in the Django ``settings.py``.

    Example:

    .. code-block:: python

        INSTALLED_APPS = (
            # ... your other installed apps
            'tags_input',
        )

3. Add the mappings to your ``settings.py`` file:

    Example:

    .. code-block:: python

        TAGS_INPUT_MAPPINGS = {
            'some_app.SomeKeyword': {
                'field': 'some_field',
            },
            'some_app.SomeOtherKeyword': {
                'fields': ('some_field', 'some_other_field'),
            },
            'some_app.SomeSortedKeyword': {
                'field': 'some_field',
                'ordering': [
                    'some_field',
                    'some_other_field',
                ],
                'filters': {
                    'some_field__istartswith': 'a',
                },
                'excludes': {
                    'some_field__iexact': 'foobar',
                },
            },
            'some_app.SomeCreateableKeyword': {
                'field': 'some_field',
                'create_missing': True,
            },
        }

4. Add the ``tags_input`` urls to your ``urls.py``:

    Example:

   .. code-block:: python

      from django.conf import urls

      urlpatterns = patterns('',
          url(r'^tags_input/', include('tags_input.urls', namespace='tags_input')),
          # ... other urls ... 
      )


Admin usage
-----------

.. code-block:: python

    from django.contrib import admin
    import models
    from tags_input import admin as tags_input_admin

    class YourAdmin(tags_input_admin.TagsInputAdmin):
        pass

    admin.site.register(models.YourModel, YourAdmin)


