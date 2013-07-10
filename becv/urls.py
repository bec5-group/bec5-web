from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.auth.views import logout

urlpatterns = patterns('',
    url(r'^$', 'becv.views.home', name='home'),

    url(r'^accounts/login/$', 'becv.views.login'),
    url(r'^accounts/logout/$', logout),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/')),
    url(r'^favicon.ico$', RedirectView.as_view(url='/static/img/favicon.png')),

    # admin
    url(r'^admin/', include(admin.site.urls)),
    # admin documentation
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # action log
    url(r'^json-view/', include('json_view.urls')),

    # oven controller
    url(r'^oven-control/', include('oven_control.urls')),
)
