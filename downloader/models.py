from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Upload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploadID = models.CharField(blank=False, null=False, max_length=32)
    filename = models.CharField(blank=True, null=False, max_length=256)#original name of file
    tempname = models.CharField(blank=False, null=False, max_length=256)#name of file in temp directory
    store = models.PositiveSmallIntegerField(blank=False, null=False)
    extension = models.CharField(blank=True, null=False, max_length=6)
    date = models.DateTimeField(auto_now_add=True)
    activeTime = models.DateTimeField(blank=False, null=False)
    expectedChunk = models.PositiveSmallIntegerField(default=0, blank=False, null=False)
    private = models.BooleanField(default=False, blank=False, null=False)
    board = models.PositiveSmallIntegerField(blank=False, null=False)
    url = models.URLField(blank=False, null=False, max_length=1024)
    title = models.CharField(blank=False, null=False, max_length=256)
    
    downloadType = models.CharField(blank=False, null=False, max_length=16)
    status = models.CharField(blank=False, null=False, max_length=16)
    description = models.TextField(blank=True, null=False)
    priority = models.CharField(blank=False, null=False, max_length=16)
    filesize = models.PositiveIntegerField(blank=False, null=False)
    
    def __str__(self):
        return '{0!s} / {1!s} / {2!s} --- {3!s} --- {4!s}'.format(self.activeTime, self.priority, self.status, self.downloadType, self.url)