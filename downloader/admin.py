from django.contrib import admin

from .models import Upload

# Register your models here.

def set_to_waiting_temp_func(modeladmin, request, queryset):
    queryset.update(status='Waiting')
set_to_waiting_temp_func.short_description = "Set as waiting"

def set_to_low(modeladmin, request, queryset):
    queryset.update(priority='Low')
set_to_waiting_temp_func.short_description = "Set to low prio"

def set_to_high(modeladmin, request, queryset):
    queryset.update(priority='High')
set_to_waiting_temp_func.short_description = "Set to high prio"

class UploadAdmin(admin.ModelAdmin):
    list_display = ['activeTime', 'priority', 'status', 'downloadType', 'url']
    ordering = ['-activeTime']
    actions = [set_to_waiting_temp_func, set_to_low, set_to_high]
    
admin.site.register(Upload, UploadAdmin)