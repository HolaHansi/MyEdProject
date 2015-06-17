from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^pc/$',
        view = views.PCListView.as_view(),
        name="PC_API"),
    url(r'^pc/(?P<id>\d+)/$',
        view=views.PCRetrieveView.as_view(),
        name="PC_API")
    ]


