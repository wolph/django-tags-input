from django.conf import urls
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    urls.url(r'^', urls.include('example.demo.urls')),
    urls.url(r'^tags_input/',
             urls.include('tags_input.urls', namespace='tags_input')),
    urls.url(r'^admin/doc/', urls.include('django.contrib.admindocs.urls')),
    urls.url(r'^admin/', admin.site.urls),
]

