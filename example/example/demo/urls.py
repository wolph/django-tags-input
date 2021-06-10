from django.conf import urls
from example.demo import views

app_label = 'example.demo'
urlpatterns = [
    urls.url(r'^$', views.index, name='index'),
]


