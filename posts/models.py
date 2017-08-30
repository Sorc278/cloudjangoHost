from __future__ import unicode_literals
import shutil

from django.db import models
from django.contrib.auth.models import User

from cloudjangohost.settings import MEDIA_ROOT, MEDIA_URL, SITE_BASE

from storage.operations import get_post_path_by_post, get_thumb_path_by_post
from managers.extHelpers import get_extension_type
from managers import imageManager

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(blank=True, null=False, max_length=256)
    store = models.PositiveSmallIntegerField(blank=False, null=False)
    filename = models.CharField(blank=False, null=False, max_length=16, unique=True)#name on disk and to be referenced with
    extension = models.CharField(blank=False, null=False, max_length=6)
    date = models.DateTimeField(auto_now_add=True)
    private = models.BooleanField(default=False, blank=False, null=False)
    board = models.PositiveSmallIntegerField(blank=False, null=False)
    source = models.TextField(blank=False, null=False)
    size = models.IntegerField(blank=False, null=False)
    
    def __str__(self):
        return self.date.__str__() + ' - ' + self.filename
    
    def url_thumb(self):
        return '{0!s}{1!s}'.format(SITE_BASE, get_thumb_path_by_post(self).replace(MEDIA_ROOT, MEDIA_URL))
    
    def url_post(self):
        return '{0!s}{1!s}'.format(SITE_BASE, get_post_path_by_post(self).replace(MEDIA_ROOT, MEDIA_URL))
        
    def human_size(self):
        for x in ['KB','MB','GB','TB']:
            if self.size < 1024.0:
                return "%3.1f%s" % (self.size, x)
            self.size /= 1024.0
            #by Fred Cirera, slighlty modified to convert from KB
            #https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size
            
    def extension_type(self):
        return get_extension_type(self.extension)
        
    def thumb_from_image(self, path):
        im = imageManager.get_thumb_in_memory(path)
        im.save(get_thumb_path_by_post(self), "JPEG", quality=90)
        
class Extra(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    extra_filename = models.PositiveSmallIntegerField(blank=False, null=False)
    description = models.CharField(blank=True, null=False, max_length=64)
    extra_type = models.CharField(blank=False, null=False, max_length=32)
    extension = models.CharField(blank=False, null=False, max_length=6)
    date = models.DateTimeField(auto_now_add=True)
    
    def save(self): 
        if self.extra_filename is None:
            top = Extra.objects.order_by('-extra_filename').first()
            self.extra_filename = top.extra_filename+1 if not top is None else 1
        super(Extra, self).save()
        
    def get_extra_path(self):
        return '{0!s}.{1!s}.{2!s}'.format(get_post_path_by_post(self.post), self.extra_filename, self.extension)
        
    def save_from_file(self, path):
        shutil.copy(path, self.get_extra_path())