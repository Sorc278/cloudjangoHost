from __future__ import unicode_literals
import shutil
import os, os.path
from cStringIO import StringIO
from PIL import Image

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from cloudjangohost.settings import MEDIA_ROOT, MEDIA_URL, SITE_BASE

import storage.operations as s
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
		
	def get_post_main(self):
		return '{0!s}{1!s}.{2!s}'.format(s.get_post_folder(self.store), self.filename, self.extension)
		
	def get_post_thumb(self):
		return '{0!s}{1!s}.jpg'.format(s.get_thumb_folder(self.store), self.filename)
	
	def url_post(self):
		return '{0!s}{1!s}'.format(SITE_BASE, self.get_post_main().replace(MEDIA_ROOT, MEDIA_URL))

	def url_thumb(self):
		if os.path.isfile(self.get_post_thumb()):
			return '{0!s}{1!s}'.format(SITE_BASE, self.get_post_thumb().replace(MEDIA_ROOT, MEDIA_URL))
		else:
			return '{0!s}static/{1!s}.png'.format(SITE_BASE, self.extension)
			
	def url_post_page(self):
		return reverse('posts:post', kwargs={'board': self.board, 'filename': self.filename})
		
	def delete_files(self):
		if os.path.isfile(self.get_post_main()):
			os.remove(self.get_post_main())
			if os.path.isfile(self.get_post_main()):
				raise OSError('Could not remove post main file')
		
		if os.path.isfile(self.get_post_thumb()):
			os.remove(self.get_post_thumb())
			if os.path.isfile(self.get_post_thumb()):
				raise OSError('Could not remove post thumb')
				
	def move_files_from(self, upload):
		if os.path.isfile(upload.get_temp_main()):
			os.rename(upload.get_temp_main(), self.get_post_main())
			if not os.path.isfile(self.get_post_main()):
				raise OSError('Could not move main file from upload to post location')
		else:
			raise OSError('Main file was not found')
		
		if os.path.isfile(upload.get_temp_thumb()):
			os.rename(upload.get_temp_thumb(), self.get_post_thumb())
			if not os.path.isfile(self.get_post_thumb()):
				raise OSError('Could not move thumb from upload to post location')
		else:
			extType = get_extension_type(upload.extension)
			if not 'music' == extType:
				raise OSError('Thumb was not found')
		
	def human_size(self):
		for x in ['KB','MB','GB','TB']:
			if self.size < 1024.0:
				return "%3.1f%s" % (self.size, x)
			self.size /= 1024.0
			#by Fred Cirera, slighlty modified to convert from KB
			#https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size
			
	def extension_type(self):
		return get_extension_type(self.extension)
		
	def thumb_from_image(self, imageData):
		im = imageManager.get_thumb_in_memory_from_memory(Image.open(StringIO(imageData)))
		im.save(self.get_post_thumb(), "JPEG", quality=90)
		
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