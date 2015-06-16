from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^api/$',
        view = views.PCCreateReadView.as_view(),
        name="PC_API"),
    url(r'^api/(?P<id>\d+)/$',
        view=views.PCReadUpdateDeleteView.as_view(),
        name="PC_API")
    ]