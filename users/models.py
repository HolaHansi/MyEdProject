from django.db import models
from django.contrib.auth.models import User
from rooms.models import Bookable_Room
from pc.models import PC_Space

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    room_favourites = models.ManyToManyField(Bookable_Room, related_name='room_fav')
    pc_favourites = models.ManyToManyField(PC_Space, related_name='pc_fav')
    room_history = models.ManyToManyField(Bookable_Room, related_name='room_his')
    pc_history = models.ManyToManyField(PC_Space, related_name='pc_hist')

    # for testing
    is_a_john = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username

class Entry(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    moderator = models.ForeignKey(User)
    id = models.IntegerField(primary_key=True)

    def __string__(self):
        return self.title

    def __unicode__(self):
        return self.title




# Create your models here.
