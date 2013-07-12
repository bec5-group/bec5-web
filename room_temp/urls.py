from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^get-servers/$', views.get_servers),
    url(r'^get-server-setting/(?P<sid>[^/]*)/$', views.get_server_setting),

    url(r'^add-server/$', views.add_server),
    url(r'^edit-server/(?P<sid>[^/]*)/$', views.edit_server),
    url(r'^del-server/(?P<sid>[^/]*)/$', views.del_server),

    url(r'^get-devices/$', views.get_devices),
    url(r'^get-device-setting/(?P<did>[^/]*)/$', views.get_device_setting),

    url(r'^add-device/$', views.add_device),
    url(r'^edit-device/(?P<did>[^/]*)/$', views.edit_device),
    url(r'^del-device/(?P<did>[^/]*)/$', views.del_device),

    url(r'^get-value-logs/$', views.get_value_logs),
)
