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

from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^get-ovens/$', views.get_ovens),
    url(r'^get-ctrl-setting/(?P<cid>[^/]*)/$', views.get_controller_setting),

    url(r'^add-controller/$', views.add_controller),
    url(r'^set-controller/(?P<cid>[^/]*)/$', views.set_controller),
    url(r'^del-controller/(?P<cid>[^/]*)/$', views.del_controller),

    url(r'^get-profiles/$', views.get_profiles),
    url(r'^get-profile-setting/(?P<pid>[^/]*)/$', views.get_profile_setting),

    url(r'^add-profile/(?P<name>[^/]*)/$', views.add_profile),
    url(r'^add-profile/(?P<name>[^/]*)/(?P<order>[^/]*)/$', views.add_profile),
    url(r'^edit-profile/(?P<profile>[^/]*)/$', views.edit_profile),
    url(r'^edit-profile/(?P<profile>[^/]*)/(?P<name>[^/]*)/$',
        views.edit_profile),
    url(r'^edit-profile/(?P<profile>[^/]*)/(?P<name>[^/]*)/(?P<order>[^/]*)/$',
        views.edit_profile),
    url(r'^del-profile/(?P<pid>[^/]*)/$', views.del_profile),

    url(r'^get-temps/$', views.get_temps),
    url(r'^get-setpoint/$', views.get_setpoint),

    url(r'^set-profile/(?P<profile>[^/]*)/', views.set_profile),
    url(r'^set-temps/$', views.set_temps),

    url(r'^get-errors/$', views.get_errors),
    url(r'^get-logs/$', views.get_logs),
    url(r'^get-temp-logs/$', views.get_temp_logs),
)
