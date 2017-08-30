# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from changelog.models import ChangelogItem
from posts.models import Post
from scratchpad.models import Note
from tags.models import Tag

def migrate(username):
	userobj = User.objects.get(username=username)
	for i in Changelog.objects.all():
		i.migrate()
		print('Migrated changelog item '+str(i.changeid))
	for i in Posts.objects.all():
		i.migrate(userobj)
		print('Migrated Posts item '+str(i.postid))
	for i in Scratchpad.objects.all():
		i.migrate(userobj)
		print('Migrated Scratchpad item '+str(i.noteid))
	for i in Tags.objects.all():
		i.migrate()
		print('Migrated Tags item '+str(i.tagid))
	for i in Titles.objects.all():
		i.migrate()
		print('Migrated Titles item ')

class Changelog(models.Model):
	changeid = models.AutoField(db_column='changeID', primary_key=True)  # Field name made lowercase.
	changetitle = models.CharField(db_column='changeTitle', max_length=64)  # Field name made lowercase.
	changetext = models.CharField(db_column='changeText', max_length=5000, blank=True, null=True)  # Field name made lowercase.
	changedate = models.DateTimeField(db_column='changeDate')  # Field name made lowercase.
	sticky = models.IntegerField(blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'changelog'
		
	def migrate(self):
		i = ChangelogItem()
		i.priority = 0
		i.title = self.changetitle
		i.text = self.changetext
		i.save()
		ChangelogItem.objects.filter(pk=i.pk).update(when = self.changedate)

class Posts(models.Model):
	postid = models.AutoField(db_column='postID', primary_key=True)  # Field name made lowercase.
	userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='userID')  # Field name made lowercase.
	privatepost = models.IntegerField(db_column='privatePost')  # Field name made lowercase.
	rating = models.IntegerField()
	postdate = models.DateTimeField(db_column='postDate')  # Field name made lowercase.
	storagedisk = models.IntegerField(db_column='storageDisk')  # Field name made lowercase.
	filename = models.CharField(max_length=8)
	ftype = models.CharField(max_length=6)
	source = models.CharField(max_length=1024)
	postsize = models.IntegerField(db_column='postSize')  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = 'posts'
		
	def migrate(self, userobj):
		i = Post()
		i.user = userobj
		i.title = ''
		i.store = 1
		i.filename = self.filename+'abcd1234'
		i.extension = self.ftype
		i.private = False
		i.board = self.rating
		i.source = self.source
		i.size = self.postsize
		i.save()
		Post.objects.filter(pk=i.pk).update(date = self.postdate)

class Scratchpad(models.Model):
	noteid = models.AutoField(db_column='noteID', primary_key=True)  # Field name made lowercase.
	userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
	note = models.CharField(max_length=256)
	notedate = models.DateTimeField(db_column='noteDate')  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = 'scratchpad'
		
	def migrate(self, userobj):
		i = Note()
		i.user = userobj
		i.content = self.note
		i.date = self.notedate
		i.save()
		Note.objects.filter(pk=i.pk).update(date = self.notedate)

class Tags(models.Model):
	tagid = models.SmallIntegerField(db_column='tagID', primary_key=True)  # Field name made lowercase.
	tagname = models.CharField(db_column='tagName', unique=True, max_length=60)  # Field name made lowercase.
	tagtype = models.IntegerField(db_column='tagType')  # Field name made lowercase.
	tagdescription = models.CharField(db_column='tagDescription', max_length=500, blank=True, null=True)  # Field name made lowercase.
	minrating = models.IntegerField(db_column='minRating')  # Field name made lowercase.
	adminonly = models.IntegerField(db_column='adminOnly', blank=True, null=True)  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = 'tags'
		
	def migrate(self):
		i = Tag()
		i.name = self.tagname
		i.tag_type = self.tagtype
		i.description = self.tagdescription
		i.staff_only = False if self.adminonly is None or self.adminonly == 0 else True
		i.min_board = self.minrating
		i.occurences = 0
		i.save()

class Titles(models.Model):
	postid = models.ForeignKey(Posts, models.DO_NOTHING, db_column='postID', primary_key=True)  # Field name made lowercase.
	title = models.CharField(max_length=120)

	class Meta:
		managed = False
		db_table = 'titles'
		
	def migrate(self):
		i = Post.objects.get(filename=self.postid.filename+'abcd1234')
		i.title = self.title
		i.save()

class Users(models.Model):
	userid = models.AutoField(db_column='userID', primary_key=True)  # Field name made lowercase.
	uname = models.CharField(max_length=30)
	phash = models.CharField(max_length=256)
	salt = models.CharField(max_length=128)
	utype = models.IntegerField()
	storageused = models.IntegerField(db_column='storageUsed')  # Field name made lowercase.
	storageallowed = models.IntegerField(db_column='storageAllowed')  # Field name made lowercase.
	lastseen = models.DateTimeField(db_column='lastSeen', blank=True, null=True)  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = 'users'
