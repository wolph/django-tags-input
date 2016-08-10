from django.conf import urls
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    urls.url(r'^tags_input/',
             urls.include('tags_input.urls', namespace='tags_input')),
    urls.url(r'^admin/doc/', urls.include('django.contrib.admindocs.urls')),
    urls.url(r'^admin/', urls.include(admin.site.urls)),
]

