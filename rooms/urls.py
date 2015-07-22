from django.conf.urls import url

from rooms import views

urlpatterns = [
    url(r'^$', views.index, name='rooms'),
    url(r'^filter/$', views.filter_suggestions, name='filterRoomSuggestions')
]
