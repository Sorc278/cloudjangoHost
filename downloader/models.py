from __future__ import unicode_literals
import os.path
from ast import literal_eval

from django.db import models
from django.contrib.auth.models import User

import storage.operations as s

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
	options = models.CharField(blank=True, null=True, max_length=32768)
	
	def __str__(self):
		return '{0!s} / {1!s} / {2!s} --- {3!s} --- {4!s}'.format(self.activeTime, self.priority, self.status, self.downloadType, self.url)
		
	def store_options(self, dict):
		self.options = repr(dict)
		self.save()
		
	def get_options(self):
		return literal_eval(self.options)
		
	def prepare(self):
		try:
			s.create_folder(self.get_temp_folder())
		except Exception as e:
			raise

	def cleanup(self):
		try:
			s.delete_folder(self.get_temp_folder())
		except Exception as e:
			raise
			
	def write_chunk_from_memory(self, chunk):
		try:
			s.write_chunk_from_memory(self.get_temp_main(), chunk)
		except Exception as e:
			raise
		self.expectedChunk += 1
		self.save()
		
	def get_temp_folder(self):
		return s.get_temp_path_folder(self.store, self.tempname)
		
	def get_temp_main(self):
		return '{0!s}{1!s}.{2!s}'.format(self.get_temp_folder(), 'main', self.extension)

	def get_temp_thumb(self):
		return '{0!s}{1!s}'.format(self.get_temp_folder(), 'thumb.jpg')
		
	def main_file_present(self):
		if self.extension == 'album':
			images = self.get_options()['image_items']
			page = 0
			for image in images:
				if not os.path.isfile('{0!s}{1!s}.{2!s}'.format(self.get_temp_folder(), page, image['ext'])):
					return False
				page += 1
			return True
		else:
			return os.path.isfile(self.get_temp_main())
			
	def get_size(self):
		if self.extension == 'album':
			images = self.get_options()['image_items']
			page = 0
			size = 0
			for image in images:
				size += s.get_file_size('{0!s}{1!s}.{2!s}'.format(self.get_temp_folder(), page, image['ext']))
				page += 1
			return size
		else:
			return s.get_file_size(self.get_temp_main())
	
	def complete(self):
		self.status_update('Complete', '')
	
	def waiting(self):
		self.status_update('Waiting', '')
	
	def working(self, description):
		self.status_update('Working', description)
		
	def downloading(self, downloaded_kb):
		self.working('Downloaded {0!s} of {1!s}'.format(self.human_size(downloaded_kb), self.human_size(self.filesize)))
		
	def downloading_manual_bytes(self, downloaded_b, total_b):
		self.working('Downloaded {0!s} of {1!s}'.format(self.human_size_bytes(downloaded_b), self.human_size_bytes(total_b)))
	
	def fatal_error(self, description):
		self.status_update('Failed', description)
		self.cleanup()
		
	def status_update(self, status, description):
		self.status = status
		self.description = description
		self.save()
		
	def human_size(self, size_in_kb):
		size = size_in_kb
		for x in ['KB','MB','GB','TB']:
			if size < 1024.0:
				return "%3.1f%s" % (size, x)
			size /= 1024.0
			#by Fred Cirera, slighlty modified to convert from KB
			#https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size
			
	def human_size_bytes(self, size_in_b):
		size = size_in_b
		for x in ['B','KB','MB','GB','TB']:
			if size < 1024.0:
				return "%3.1f%s" % (size, x)
			size /= 1024.0
			#by Fred Cirera, slighlty modified to convert from KB
			#https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size