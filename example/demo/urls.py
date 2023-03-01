from django import urls

from example.demo import views

app_label = 'example.demo'
urlpatterns = [
    urls.re_path(r'^$', views.index, name='index'),
]
