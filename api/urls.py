from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^pc/$',
        view = views.PCCreateReadView.as_view(),
        name="PC_API"),
    url(r'^pc/(?P<id>\d+)/$',
        view=views.PCReadUpdateDeleteView.as_view(),
        name="PC_API")
    ]


