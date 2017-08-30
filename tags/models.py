from __future__ import unicode_literals

from django.db.models import Q
from django.db.models import Sum
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from posts.models import Post

# Create your models here.
class Tag(models.Model):
	name = models.CharField(blank=False, null=False, max_length=64, unique=True)
	tag_type = models.PositiveSmallIntegerField(blank=False, null=False)
	description = models.TextField(blank=False, null=False)
	staff_only = models.BooleanField(default=False, blank=False, null=False)
	min_board = models.PositiveSmallIntegerField(blank=False, null=False)
	posts = models.ManyToManyField(Post, blank=True, editable=False)
	occurences = models.IntegerField(blank=False, null=False, default=0)
	
	def __str__(self):
		return self.name
	
	def increment_occurences(self):
		self.occurences += 1
		self.save(update_fields=['occurences'])
	
	class Meta:
		indexes = [
			models.Index(fields=['name']),
		]
	
class PostTag(models.Model):
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	added_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
	date = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		indexes = [
			models.Index(fields=['post', 'tag']),
		]
	
class TagChance(models.Model):
	parent = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='parent')
	child = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='child')
	child_num = models.IntegerField(blank=False, null=False, default=0)
	
	def __str__(self):
		return self.parent.__str__()+'--'+self.child.__str__()+'  #'+str(self.child_num)
	
	def percent(self):
		return int((100*self.child_num)/self.parent.occurences)
	
	def soft_set_tags(self, tag1, tag2):
		if tag1.name <= tag2.name:
			self.parent = tag1
			self.child = tag2
		else:
			self.parent = tag2
			self.child = tag1
			
	class Meta:
		indexes = [
			models.Index(fields=['parent']),
			models.Index(fields=['child']),
		]
		
		
class TagSuggestion(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
	
	def percent(self):
		occ = self.post.tag_set.aggregate(Sum('occurences'))['occurences__sum']
		if occ is None:
			return 0
		tag_set = self.post.tag_set.values_list('id', flat=True)
		ch_occ = TagChance.objects.filter(Q(parent__in=tag_set, child=self.tag) | Q(parent=self.tag, child__in=tag_set)).aggregate(Sum('child_num'))['child_num__sum']
		if ch_occ is None:
			return 0
		return int((100*ch_occ)/occ)
		
	class Meta:
		indexes = [
			models.Index(fields=['post']),
			models.Index(fields=['post', 'tag']),
		]

@receiver(post_save, sender=Tag)
def add_tag_suggestions(sender, instance, created, **kwargs):
	if created:
		bulk_list = []
		for post in Post.objects.all():
			i = TagSuggestion()
			i.tag = instance
			i.post = post
			bulk_list.append(i)
		TagSuggestion.objects.bulk_create(bulk_list)
		
		bulk_tag_chances = []
		for tag in Tag.objects.exclude(id=instance.id):
			i = TagChance()
			i.soft_set_tags(instance, tag)
			i.child_num = 0
			bulk_tag_chances.append(i)
		TagChance.objects.bulk_create(bulk_tag_chances)
		
		tags = Tag.objects.all()
		tag_dict = {}
		i = 0
		for tag in tags:
			tag_dict[i] = tag.name
			i += 1
			
		import json
		from cloudjangohost.settings import TAG_DICT_PATH
		with open(TAG_DICT_PATH, 'w') as fp:
			json.dump(tag_dict, fp)

@receiver(post_save, sender=Post)          
def add_suggestions_to_post(sender, instance, created, **kwargs):
	if created:
		bulk_list = []
		for tag in Tag.objects.all():
			i = TagSuggestion()
			i.tag = tag
			i.post = instance
			bulk_list.append(i)
		TagSuggestion.objects.bulk_create(bulk_list)

#class tagDeletion(models.Model)
	# user = models.ForeignKey(User, on_delete=models.PROTECT)
	# title = models.CharField(blank=True, null=False, max_length=256)
	# store = models.PositiveSmallIntegerField(blank=False, null=False)
	# filename = models.CharField(blank=False, null=False, max_length=16)#name on disk and to be referenced with
	# extension = models.CharField(blank=False, null=False, max_length=6)
	# date = models.DateTimeField(auto_now_add=True)
	# private = models.BooleanField(default=False, blank=False, null=False)
	# board = models.PositiveSmallIntegerField(blank=False, null=False)
	# source = models.TextField(blank=False, null=False)
	# size = models.IntegerField(blank=False, null=False)