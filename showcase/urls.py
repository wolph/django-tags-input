"""Native forms, admin and the package autocomplete endpoint."""

from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

from .views import index

urlpatterns: list[URLPattern | URLResolver] = [
    path('', index, name='showcase'),
    path('admin/', admin.site.urls),
    path('tags-input/', include('tags_input.urls')),
]
