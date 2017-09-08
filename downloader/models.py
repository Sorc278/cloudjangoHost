from __future__ import unicode_literals
import os.path

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
	
	def __str__(self):
		return '{0!s} / {1!s} / {2!s} --- {3!s} --- {4!s}'.format(self.activeTime, self.priority, self.status, self.downloadType, self.url)
		
	def prepare(self):
		try:
			s.create_folder(self.get_temp_folder())
		except Exception as e:
			raise e

	def cleanup(self):
		try:
			s.delete_folder(self.get_temp_folder())
		except Exception as e:
			raise e
			
	def write_chunk_from_memory(self, chunk):
		try:
			s.write_chunk_from_memory(self.get_temp_main(), chunk)
		except Exception as e:
			raise e
		
	def get_temp_folder(self):
		return s.get_temp_path_folder(self.store, self.tempname)
		
	def get_temp_main(self):
		return '{0!s}{1!s}.{2!s}'.format(self.get_temp_folder(), 'main', self.extension)

	def get_temp_thumb(self):
		return '{0!s}{1!s}'.format(self.get_temp_folder(), 'thumb.jpg')
		
	def main_file_present(self):
		return os.path.isfile(self.get_temp_main())
	
	def complete(self):
		self.status_update('Complete', '')
	
	def waiting(self):
		self.status_update('Waiting', '')
	
	def working(self, description):
		self.status_update('Working', description)
	
	def fatal_error(self, description):
		self.status_update('Failed', description)
		self.cleanup()
		
	def status_update(self, status, description):
		self.status = status
		self.description = description
		self.save()