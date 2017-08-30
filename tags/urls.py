from django.conf.urls import url

from . import views

app_name = 'tags'

urlpatterns = [
	url(r'^add_tag$', views.add_tag, name='add_tag'),
	url(r'^get_suggested_tags_json$', views.get_suggested_tags_json, name='get_suggested_tags_json'),
	url(r'^add_suggested_tag$', views.add_suggested_tag, name='add_suggested_tag'),
	url(r'^remove_suggested_tag$', views.remove_suggested_tag, name='remove_suggested_tag'),
	url(r'^tag_list$', views.tag_list, name='tag_list'),
	url(r'^tag_description/(?P<tag>.*)$', views.tag_description, name='tag_description'),
]