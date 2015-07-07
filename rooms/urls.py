from django.conf.urls import url

from rooms import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^filter/$', views.filter_suggestions, name='filterSuggestions')
]
