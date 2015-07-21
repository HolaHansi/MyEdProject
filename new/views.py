from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return render(request, 'new/core/index.html')


def pc_index(request):
    return render(request, 'new/pc/index.html')


def rooms_index(request):
    return render(request, 'new/rooms/index.html')


@login_required
def users_favourites(request):
    user = request.user
    pc_favourites = user.pc_favourites.all()
    room_favourites = user.room_favourites.all()
    context = {'pc_favourites': pc_favourites,
               'room_favourites': room_favourites,
               'user': user}
    return render(request, 'new/users/favourites.html', context)
