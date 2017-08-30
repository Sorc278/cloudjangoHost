from django.conf.urls import url

from . import views

app_name = 'welcome'

urlpatterns = [
	url(r'^$', views.login_page, name='login'),
	url(r'^logout$', views.logout_page, name='logout'),
	url(r'^register$', views.register, name='register'),
]