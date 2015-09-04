"""MyEd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url

urlpatterns = [
    # webpages:

    # homepage
    url(r'^$', 'users.views.index', name='home'),
    # labs suggester page and API
    url(r'^labs/', include('pc.urls'), name='labs'),
    # rooms suggester page and API
    url(r'^rooms/', include('rooms.urls'), name='rooms'),
    # favourite page
    url(r'^favourites/$', 'users.views.favourites', name='favourites'),
    # history page
    url(r'^history/$', 'users.views.history', name='history'),
    # 'open link in new window' view for displaying in myed
    url(r'^myed/$', 'myed.views.index', name='myEdDesktop'),

    # APIs:

    # get data for calendar
    url(r'^calendar/$', 'users.views.calendar', name='calendar'),
    # get the HTML for a favourites panel
    url(r'^favourites/panel/$', 'users.views.get_panel', name='panel'),
    # like/unlike a location
    url(r'^like/', 'users.views.like'),
    # get all this user's favourite labs or rooms
    url(r'^getLiked/', 'users.views.get_all_favourites'),
    # registration (only used in development)
    url(r'^registration/$', 'users.views.register'),
    # log out
    url(r'^logout/$', 'users.views.logout'),
    # log in (only used in development)
    url(r'login/$', 'users.views.login'),
    # get data for autocomplete dropdown
    url(r'autocompleteAPI/', 'users.views.autocompleteAPI')
]
