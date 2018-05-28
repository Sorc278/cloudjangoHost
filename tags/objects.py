from django.contrib.auth.models import User

from .models import Tag, PostTag, TagDeclination
from posts.models import Post

class TaggablePost:
	
	def __init__(self, post, working_user):
		self.post = post if isinstance(post, Post) else Post.objects.get(filename=post)
		self.user = working_user if isinstance(working_user, User) or working_user is None else User.objects.get(pk=working_user)
		
	def get_tag_list(self):
		return list(self.post.tag_set.values_list('id', flat=True))
		
	def get_tag_declination_list(self):
		return list(TagDeclination.objects.filter(post=self.post).values_list('tag_id', flat=True))
		
	def get_possible_tag_list(self):
		all_tags = set(Tag.objects.values_list('id', flat=True))
		tags = set(self.get_tag_list())
		declined_tags = set(self.get_tag_declination_list())
		return list(all_tags - tags - declined_tags)
	
	def add_tag(self, tag_to_add):
		tag = tag_to_add if isinstance(tag_to_add, Tag) else Tag.objects.get(name=tag_to_add)
		
		if tag.staff_only and not self.user.is_staff:
			#TODO: add message that tag can be used only by admin and make it a security exception. Make using funcs change response code depending on this
			raise ValueError("User is not set as staff")
			
		if not PostTag.objects.filter(post=self.post, tag=tag).exists():
			tag.increment_occurences()
			tag.posts.add(self.post)
			PostTag.objects.create(tag=tag, post=self.post, added_by=self.user)
			if TagDeclination.objects.filter(post=self.post, tag=tag).exists():
				TagDeclination.objects.filter(post=self.post, tag=tag).delete()

	def add_tag_declination(self, tag_to_decline):
		tag = tag_to_decline if isinstance(tag_to_decline, Tag) else Tag.objects.get(name=tag_to_decline)
		TagDeclination.objects.create(tag=tag, post=self.post)