from django.conf.urls import url
from ssh_search import views

urlpatterns = [
    url(r'^$', views.index, name='index')
]
