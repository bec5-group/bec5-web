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

"""
Main view. Please keep this file as small as possible and
put anything (e.g. jsonp api requests/views/urls) to a separate app.
See below for examples.
"""

from django.shortcuts import render
from django.contrib.auth import views as auth_views

_login = auth_views.login

def login(req, *args, **kwargs):
    if req.method == 'POST' and not req.POST.get('remember', None):
        req.session.set_expiry(0)
    return _login(req, *args, **kwargs)
auth_views.login = login

def to_user_obj(user):
    if user.is_authenticated():
        return {
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    return {}

def home(request):
    user = request.user
    logged_in = user.is_authenticated()
    return render(request, 'home.html', {
        'action_permissions': {
            'oven-control': user.has_perm('oven_control.set_profile'),
            'oven-temp': True,
            'oven-settemp': user.has_perm('oven_control.set_temp'),
            'oven-setprofile-temp': user.has_perm(
                'oven_control.set_profile_temp'),
            'oven-setcontroller': user.has_perm('oven_control.set_controller'),
            'oven-temp-log': logged_in,
            'oven-action-log': logged_in,
            'room-temp-log': logged_in,
            'oven-ctrl-log': logged_in,
            'room-temp-edit-server': user.has_perm('room_temp.edit_server'),
        },
        'user_obj': to_user_obj(user)
    })
