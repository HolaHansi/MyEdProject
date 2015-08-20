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
from django.contrib import admin


urlpatterns = [
    url(r'^$', 'users.views.index', name='home'),
    url(r'^labs/', include('pc.urls'), name='labs'),
    url(r'^rooms/', include('rooms.urls'), name='rooms'),
    url(r'^favourites/$', 'users.views.favourites', name='favourites'),
    url(r'^history/$', 'users.views.history', name='history'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^calendar/$', 'users.views.calendar', name='calendar'),
    url(r'^favourites/panel/$', 'users.views.get_panel',name='panel'),
    url(r'^like/', 'users.views.like'),
    url(r'^getLiked/', 'users.views.get_all_favourites'),
    url(r'^registration/$', 'users.views.register'),
    url(r'^logout/$', 'users.views.logout'),
    url(r'login/$', 'users.views.login'),
    # url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'auth/login.html'})
    url(r'autocompleteAPI/', 'users.views.autocompleteAPI')
]
