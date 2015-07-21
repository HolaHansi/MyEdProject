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
    url(r'^$', include('users.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^open/', include('pc.urls')),
    url(r'^bookable/', include('rooms.urls')),
    url(r'^api/', include('api.urls')),

    url(r'^favourites/$', 'users.views.favourites'),
    url(r'^like/', 'users.views.like'),
    url(r'^registration/$', 'users.views.register'),
    url(r'^logout/$', 'users.views.logout'),
    url(r'login/$', 'users.views.login'),
    # url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'auth/login.html'})
    url(r'autocompleteAPI/','users.views.autocompleteAPI'),

    url(r'new/',include('new.urls'))
]
