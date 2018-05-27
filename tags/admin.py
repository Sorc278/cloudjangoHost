from django.contrib import admin

from .models import Tag, PostTag, TagDeclination

# Register your models here.
admin.site.register(Tag)
admin.site.register(PostTag)
admin.site.register(TagDeclination)