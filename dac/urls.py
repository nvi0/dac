from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.home),
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^fooview/(?P<foo_id>\d+)/$', views.fooview),
    url(r'^upload/$', views.uploadfile),
    # url(r'^accounts/$', include('registrations.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/manage_file/$', views.manage_file),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/password_change/$','django.contrib.auth.views.password_change',{'post_change_redirect':'/accounts/profile'}),
    url(r'^accounts/register/$', views.registration),
    url(r'^testfileview$', views.fileview),
)
