from django.conf.urls import patterns, include, url
from dac.uploader import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^admin/$', views.admin),
                       url(r'^admin/edit_positions/$', views.admin_edit_positions),
                       url(r'^admin/create_user/$', views.admin_create_user),
                       
                       url(r'^upload/$', views.upload_file),
                       url(r'^login/$', views.intropage),
                       url(r'^upload/confirm/$', views.confirm_upload_file),
                       url(r'^personal/$', views.manage_file),
                       url(r'^personal/delete/(?P<aid>\d+)/$', views.delete_one_file),
                       url(r'^personal/delete/$', views.delete_selected_files),
                       url(r'^download/(?P<aid>\d+)/$', views.send_one_file),
                       url(r'^personal/edit_tag/$', views.edit_tag),
                       url(r'^personal/edit_title/$', views.edit_title),
                       
                       )
