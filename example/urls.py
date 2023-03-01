from django import urls
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    urls.re_path(r'^', urls.include('example.demo.urls')),
    urls.re_path(r'^tags_input/',
             urls.include('tags_input.urls', namespace='tags_input')),
    urls.re_path(r'^admin/doc/', urls.include('django.contrib.admindocs.urls')),
    urls.re_path(r'^admin/', admin.site.urls),
]

