from django.conf.urls import patterns, url

urlpatterns = patterns('tags_input.views',
    url(r'^autocomplete/(?P<app>\w+)/(?P<model>\w+)/(?P<fields>[\w-]+)/$',
        'autocomplete', name='autocomplete'),
)

