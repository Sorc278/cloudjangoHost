from django.conf.urls import url

from . import views

app_name = 'chat'

urlpatterns = [
	url(r'^get_users_online$', views.get_users_online, name='get_users_online'),
	url(r'^get_chat$', views.get_chat, name='get_chat'),
	url(r'^post_message$', views.post_message, name='post_message'),
]