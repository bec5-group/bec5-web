from __future__ import print_function, division

from django.http import HttpResponse
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
from django.contrib.auth import views as auth_views

import room_temp.models as room_models
from room_temp.server import server_logger

from becv_utils import print_except
import json

from json_view import return_jsonp, auth_jsonp

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
        },
        'user_obj': to_user_obj(user)
    })
