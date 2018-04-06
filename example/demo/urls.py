from django.conf import urls
from . import views

urlpatterns = [
    urls.url(r'^$', views.index, name='index'),
]


