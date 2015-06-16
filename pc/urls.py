__author__ = 'hanschristiangregersen'

from django.conf.urls import url

from pc import views

urlpatterns = [
    url(r'^api/$',
        view = views.PCCreateReadView.as_view(),
        name="PC_API"),
    url(r'^api/(?P<id>\d+)/$',
        view=views.PCReadUpdateDeleteView.as_view(),
        name="PC_API"),

    url(r'^$', views.index, name='index'),
    url(r'^get_group/(?P<group>\w{0,50})/$', views.get_group, name='group')
]
