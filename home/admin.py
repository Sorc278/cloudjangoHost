from django.contrib import admin

from .models import Quote, ApiKey

# Register your models here.
admin.site.register(Quote)
admin.site.register(ApiKey)