__author__ = 'hanschristiangregersen'

from django.conf.urls import url

from rooms import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
