#   Copyright (C) 2013~2013 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
