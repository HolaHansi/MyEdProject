from django.db import models
from django.contrib.auth.models import AbstractUser
from rooms.models import Tutorial_Room
from pc.models import Computer_Labs

class User(AbstractUser):
    room_favourites = models.ManyToManyField(Tutorial_Room, related_name='room_fav')
    pc_favourites = models.ManyToManyField(Computer_Labs, related_name='pc_fav')
    room_history = models.ManyToManyField(Tutorial_Room, related_name='room_his', through='RoomHistory')

    def __unicode__(self):
        return self.user.username


# These are the attributes pertaining to the relation between room and user (history)
class RoomHistory(models.Model):
    booked_at_time = models.DateTimeField(null=True)
    room = models.ForeignKey(Tutorial_Room)
    user = models.ForeignKey(User)

    # could potentially add in the room-booking link