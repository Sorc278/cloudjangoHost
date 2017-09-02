from celery import shared_task

from django.contrib.auth.models import User

from .models import Tag, TagSuggestion, PostTag
from posts.models import Post

from django.db.models import F
from django.db.models import Q

@shared_task()
def process_tag_add(post_name, tag_name, user_id):
	post = Post.objects.get(filename=post_name)
	tag = Tag.objects.get(name=tag_name)
	user = User.objects.get(pk=user_id)
	
	if tag.staff_only and not user.is_staff:
		#TODO: add message that tag can be used only by admin and make it a security exception. Make using funcs change response code depending on this
		raise ValueError("User is not set as staff")
		
	if not PostTag.objects.filter(post=post, tag=tag).exists():
		tag.increment_occurences()
		PostTag.objects.create(tag=tag, post=post, added_by=user)
		tag.posts.add(post)
		TagSuggestion.objects.filter(post=post, tag=tag).delete()

@shared_task()		
def process_tag_remove(post_name, tag_name, user_id):
# 	post = Post.objects.get(filename=post_name)
# 	tag = Tag.objects.get(name=tag_name)
# 	user = User.objects.get(pk=user_id)
	
	TagSuggestion.objects.filter(post__filename=post_name, tag__name=tag_name).delete()