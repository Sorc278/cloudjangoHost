# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    content = models.TextField(blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)