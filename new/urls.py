from django.conf.urls import url
from new import views

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^labs/$', views.pc_index, name='labs'),
    url(r'^labs/filter/$', 'pc.views.filter_suggestions'),
    url(r'^rooms/$', views.rooms_index, name='rooms'),
    url(r'^rooms/filter/$', 'rooms.views.filter_suggestions'),

    url(r'^favourites/$', views.users_favourites, name='favourites'),
    url(r'^history/$', views.users_history, name='history'),
    url(r'^like/', 'users.views.like'),
    url(r'^registration/$', 'users.views.register'),
    url(r'^logout/$', 'users.views.logout'),
    url(r'login/$', 'users.views.login'),
    url(r'autocompleteAPI/','users.views.autocompleteAPI')
]
