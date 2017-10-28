from __future__ import unicode_literals
import shutil
import os, os.path, sys
if sys.version_info[0] < 3:
	from cStringIO import StringIO as pilIO
else:
	from io import BytesIO as pilIO
from PIL import Image
from ast import literal_eval

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
	
	options = models.CharField(blank=True, null=True, max_length=2048)
	
	def __str__(self):
		return self.date.__str__() + ' - ' + self.filename
		
	def store_options(self, dict):
		self.options = repr(dict)
		self.save()
		
	def get_options(self):
		return literal_eval(self.options)
		
	def get_folder(self):
		return '{0!s}{1!s}/'.format(s.get_post_folder(self.store), self.filename)
		
	def get_post_main(self):
		return '{0!s}main.{1!s}'.format(self.get_folder(), self.extension)
		
	def get_post_thumb(self):
		return '{0!s}thumb.jpg'.format(self.get_folder())
		
	def url_return_as(self, path):
		return '{0!s}{1!s}'.format(SITE_BASE, path.replace(MEDIA_ROOT, MEDIA_URL))
	
	def url_folder(self):
		return self.url_return_as(self.get_folder())

	def url_post(self):
		return self.url_return_as(self.get_post_main())

	def url_thumb(self):
		p = self.get_post_thumb()
		ret = self.url_return_as(p) if os.path.isfile(p) else '{0}static/{1}.png'.format(SITE_BASE, self.extension)
		return ret
			
	def url_post_page(self):
		return reverse('posts:post', kwargs={'board': self.board, 'filename': self.filename})
		
	def delete_files(self):
		try:
			 s.delete_folder(self.get_folder())
		except Exception as e:
			raise OSError('Could not remove post files')
				
	def move_files_from(self, upload):
		s.create_folder(self.get_folder())
		
		if upload.extension == 'album':
			path = self.get_folder()
			images = self.get_options()['images']
			for image in images:
				new_path = '{0!s}{1!s}'.format(path, image['path'])
				temp_path = '{0!s}{1!s}'.format(upload.get_temp_folder(), image['path'])
				s.move_file(temp_path, new_path)
		else:
			s.move_file(upload.get_temp_main(), self.get_post_main())
		
		if os.path.isfile(upload.get_temp_thumb()):
			s.move_file(upload.get_temp_thumb(), self.get_post_thumb())
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
		im = imageManager.get_thumb_in_memory_from_memory(Image.open(pilIO(imageData)))#pilIO is imported ByteIO or SytingIO
		im.save(self.get_post_thumb(), "JPEG", quality=90)
		
	# def legacy_to_new_format(self):
	# 	old_main = self.get_folder()[:-1] + "." + self.extension
	# 	old_thumb = self.get_folder()[:-1][:-17][:-4] + "thumb/" +self.filename + ".jpg"
	# 	if os.path.isfile(old_main):
	# 		s.create_folder(self.get_folder())
	# 		os.rename(old_main, self.get_post_main())
	# 		if os.path.isfile(old_thumb):
	# 			os.rename(old_thumb, self.get_post_thumb())
		
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