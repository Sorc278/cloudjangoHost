from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Quote(models.Model):
	quote = models.TextField(blank=False, null=False)
	source = models.TextField(blank=False, null=False)
	
	def __str__(self):
		return '{0!s} - {1!s}'.format(self.quote, self.source)
		
class ApiKey(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	key = models.CharField(blank=False, null=False, max_length=36)
	
	def __str__(self):
		return '{0!s} - {1!s}'.format(self.user, self.key)