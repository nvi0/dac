from django.conf.urls import patterns, include, url
from dac.uploader import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^personal/$', views.manage_file),
                       url(r'^personal/delete/(?P<aid>\d+)/$', views.delete_one_file),
                       url(r'^personal/delete/$', views.delete_selected_files),
                       url(r'^upload/$', views.upload_file),
                       url(r'^download/(?P<aid>\d+)/$', views.send_one_file),
                       )
