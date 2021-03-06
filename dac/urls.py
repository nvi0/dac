from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', views.home),
                       url(r'^cas_redirect/$', views.cas_redirect),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^dac/', include('dac.uploader.urls')),

#                       url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
#                       url(r'^logout/$','django.contrib.auth.views.logout_then_login'),
                       url(r'^login/$', 'djangocas.views.login'),
                       url(r'^logout/$','djangocas.views.logout'),
                       )
