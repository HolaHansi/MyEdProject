from django.db import models
from django.contrib.auth.models import AbstractUser
from rooms.models import Tutorial_Room
from pc.models import PC_Space


class User(AbstractUser):
    room_favourites = models.ManyToManyField(Tutorial_Room, related_name='room_fav')
    pc_favourites = models.ManyToManyField(PC_Space, related_name='pc_fav')
    room_history = models.ManyToManyField(Tutorial_Room, related_name='room_his')
    pc_history = models.ManyToManyField(PC_Space, related_name='pc_hist')

    def __unicode__(self):
        return self.user.username


