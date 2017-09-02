from django.contrib import admin

from .models import Tag, PostTag, TagSuggestion

# Register your models here.
admin.site.register(Tag)
admin.site.register(PostTag)
admin.site.register(TagSuggestion)