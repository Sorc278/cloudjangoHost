from django.conf.urls import url

from . import views

app_name = 'scratchpad'

urlpatterns = [
	url(r'^$', views.show_notes, name='show_notes'),
]