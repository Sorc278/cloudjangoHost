from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Create your models here.
class InvitationKey(models.Model):
    key_value = models.CharField(max_length=60, blank=False, null=False)
    
class Storage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    storage_allowed = models.BigIntegerField(default=4000000, blank=False, null=False)
    storage_used = models.BigIntegerField(default=0, blank=False, null=False)
    
@receiver(post_save, sender=User)
def save_user_storage(sender, instance, created, **kwargs):
    if created:
        Storage.objects.create(user=instance)