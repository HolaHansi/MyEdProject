from django.conf.urls import url

from frontpageApp import views

urlpatterns = [
    url(r'^$', views.index, name='index')
]
