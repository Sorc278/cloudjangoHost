from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    when = models.DateTimeField(auto_now_add=True)
    message = models.CharField(blank=False, null=False, max_length=500)