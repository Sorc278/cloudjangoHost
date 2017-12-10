from django.conf.urls import url

from . import views

app_name = 'home'

urlpatterns = [
	url(r'^$', views.homepage, name='homepage'),
	url(r'^profile$', views.profile, name='profile'),
	url(r'^get_CSRF$', views.get_CSRF, name='get_CSRF'),
]