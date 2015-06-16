from django.conf.urls import url

from suggesterApp import views

urlpatterns = [
    url(r'^$', views.index, name='index')
]
