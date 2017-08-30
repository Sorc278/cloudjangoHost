from django.conf.urls import url

from . import views

app_name = 'changelog'

urlpatterns = [
	url(r'^get_changelog$', views.get_changelog, name='get_changelog'),
]