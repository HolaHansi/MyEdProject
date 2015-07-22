from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return render(request, 'core/index.html')


def pc_index(request):
    return render(request, 'pc/index.html')


def rooms_index(request):
    return render(request, 'rooms/index.html')


@login_required
def users_favourites(request):
    user = request.user
    pc_favourites = user.pc_favourites.all()
    room_favourites = user.room_favourites.all()
    context = {'pc_favourites': pc_favourites,
               'room_favourites': room_favourites,
               'user': user}
    return render(request, 'users/favourites.html', context)


@login_required
def users_history(request):
    user = request.user
    pc_history = user.pc_history.all()
    room_history = user.room_history.all()
    context = {'pc_favourites': pc_history,
               'room_favourites': room_history,
               'user': user}
    return render(request, 'users/history.html', context)
