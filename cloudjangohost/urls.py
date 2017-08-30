"""cloudjangohost URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls.static import static


from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^chat/', include("chat.urls")),
    url(r'^submit/', include("submit.urls")),
    url(r'^downloader/', include("downloader.urls")),
    url(r'^posts/', include("posts.urls")),
    url(r'^changelog/', include("changelog.urls")),
    url(r'^home/', include("home.urls")),
    url(r'^tags/', include("tags.urls")),
    url(r'^scratchpad/', include("scratchpad.urls")),
    url(r'^admin/', admin.site.urls),
    url(r'^', include("welcome.urls")),
]

#urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)