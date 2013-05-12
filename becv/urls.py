from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.auth.views import logout

urlpatterns = patterns('',
    url(r'^$', 'becv.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'becv.views.login'),
    url(r'^accounts/logout/$', logout),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/')),
    url(r'^action/set-profile/(?P<profile>[^/]*)/$', 'becv.views.set_profile'),
    url(r'^action/get-profiles/$', 'becv.views.get_profiles'),
    url(r'^action/get-ovens/$', 'becv.views.get_ovens'),
    url(r'^action/get-temps/$', 'becv.views.get_temps'),
)
