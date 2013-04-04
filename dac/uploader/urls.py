from django.conf.urls import patterns, include, url
from dac.uploader import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^personal/$', views.manage_file),
                       url(r'^upload/$', views.upload_file),
                       )
