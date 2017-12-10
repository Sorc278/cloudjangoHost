from django.conf.urls import url

from . import views

app_name = 'submit'

urlpatterns = [
	url(r'^$', views.submit, name='submit'),
	url(r'^api$', views.submit_api, name='submit_api'),
	url(r'^query_youtube$', views.query_youtube, name='query_youtube'),
	url(r'^query_imgur$', views.query_imgur, name='query_imgur'),
]