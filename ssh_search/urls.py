# Django Imports
from django.conf.urls import url

# Project Imports
from ssh_search import views

urlpatterns = [
    # Render Index Page
    url(r'^$', views.index, name='index'),

    # Login with existing user
    url(r'^login/$', views.login),

    # Registering a new user
    url(r'^register/$', views.register),

    # Render Home Page to the user
    url(r'^home/$', views.home, name='home'),

    # Connect to GitHub
    url(r'^home/connect/$', views.connect, name='connect'),

    # Retrieve SSH key
    url(r'^home/retrieve/$', views.retrieve_ssh_key, name='retrieve'),

    # Logging out from the page
    url(r'^home/logout/$', views.logout),
]
