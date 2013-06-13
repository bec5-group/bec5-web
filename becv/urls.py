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

    url(r'^action/add-controller/$', 'becv.views.add_controller'),
    url(r'^action/get-ctrl-setting/(?P<cid>[^/]*)/$',
        'becv.views.get_controller_setting'),
    url(r'^action/set-controller/(?P<cid>[^/]*)/$',
        'becv.views.set_controller'),
    url(r'^action/del-controller/(?P<cid>[^/]*)/$',
        'becv.views.del_controller'),

    url(r'^action/get-profiles/$', 'becv.views.get_profiles'),
    url(r'^action/get-ovens/$', 'becv.views.get_ovens'),

    url(r'^action/set-profile/(?P<profile>[^/]*)/$', 'becv.views.set_profile'),
    url(r'^action/set-profile/(?P<profile>[^/]*)/(?P<name>[^/]*)/$',
        'becv.views.set_profile'),
    url(r'^action/set-profile/(?P<profile>[^/]*)/(?P<name>[^/]*)/(?P<order>[^/]*)/$', 'becv.views.set_profile'),

    url(r'^action/add-profile/(?P<name>[^/]*)/$', 'becv.views.add_profile'),
    url(r'^action/add-profile/(?P<name>[^/]*)/(?P<order>[^/]*)/$',
        'becv.views.add_profile'),

    url(r'^action/set-temp/(?P<cid>[^/]*)/(?P<temp>[-.0-9]*)/$',
        'becv.views.set_temp'),
    url(r'^action/get-temps/$', 'becv.views.get_temps'),
    url(r'^action/get-setpoint/$', 'becv.views.get_setpoint'),
)
