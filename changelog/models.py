from __future__ import unicode_literals

from django.db import models

# Create your models here.
class ChangelogItem(models.Model):
    priority = models.IntegerField(default=0, blank=False, null=False)
    title = models.CharField(blank=False, null=False, max_length=100)
    text = models.TextField(blank=False, null=False)
    when = models.DateTimeField(auto_now_add=True)