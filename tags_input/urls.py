"""URL patterns for tags input autocompletion."""

from django import urls

from . import views

app_name: str = 'tags_input'
urlpatterns: list[urls.URLPattern] = [
    urls.re_path(
        r'^autocomplete/(?P<app>\w+)/(?P<model>\w+)/(?P<fields>[\w-]+)/$',
        views.autocomplete,
        name='autocomplete',
    ),
]

__all__: list[str] = ['app_name', 'urlpatterns']
