from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Create your models here.
class LastSeen(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    when = models.DateTimeField(blank=True, null=True)
    
@receiver(post_save, sender=User)
def save_user_lastseen(sender, instance, created, **kwargs):
    if created:
        LastSeen.objects.create(user=instance)
    else:
        instance.lastseen.save()