from django.conf.urls import url

from . import views

app_name = 'downloader'

urlpatterns = [
	url(r'^queue$', views.queue, name='queue'),
	url(r'^extra/(?P<board>[1-5]{1})/(?P<filename>[0-9a-f]{16})$', views.extra, name='extra'),
	url(r'^submit_extra/(?P<board>[1-5]{1})/(?P<filename>[0-9a-f]{16})$', views.submit_extra, name='submit_extra'),
]