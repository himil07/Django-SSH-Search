from django.conf.urls import url
from ssh_search import views

urlpatterns = [
    # Render Index Page
    url(r'^$', views.index, name='index'),

    # Render Home Page to the user
    url(r'^home/$', views.home, name='home'),

    # Connect to GitHub
    url(r'^home/connect/$', views.connect, name='connect'),

    # Retrieve SSH key
    url(r'^home/retrieve/$', views.retrieve_ssh_key, name='retrieve')
]
