from django.conf.urls import url

from . import views

app_name = 'posts'

urlpatterns = [
	url(r'^(?P<board>[1-5])/(?P<page>[0-9]+)$', views.show_posts, name='posts'),
	url(r'^post/(?P<board>[1-5]{1})/(?P<filename>[0-9a-f]{16})$', views.show_post, name='post'),
]