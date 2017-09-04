from django.conf.urls import url

from . import views

app_name = 'submit'

urlpatterns = [
	url(r'^$', views.submit, name='submit'),
	url(r'^query_youtube$', views.query_youtube, name='query_youtube'),
]