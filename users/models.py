from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    is_a_john = models.BooleanField(default=True)

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
