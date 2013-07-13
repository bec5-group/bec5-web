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

    # room temperature
    url(r'^room-temp/', include('room_temp.urls')),
)
