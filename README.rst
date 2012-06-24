Overview
--------

Django Tags Input is a module that gives you a modified version of the `Xoxco jQuery Tags Input`_ library within Django.

The result is a very pretty interface with tags and autocomplete which can optionally automatically create new items when they are missing.

.. _Xoxco jQuery Tags Input: http://xoxco.com/projects/code/tagsinput/

Admin usage
-----------

.. code:: python

    from django.contrib import admin
    import models
    from tags_input import admin as tags_input_admin

    class YourAdmin(tags_input_admin.TagsInputAdmin):
        pass

    admin.site.register(models.YourModel, YourAdmin)

