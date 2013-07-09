from __future__ import print_function, division

from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
from django.contrib.auth import views as auth_views

import oven_control.models as oven_models
from oven_control.controller import ctrl_logger

from becv_utils import print_except
from logger import TimeLogger
import settings

auth_logger = TimeLogger(filename_fmt='auth_action_log-%Y-%m-%d.json',
                         dirname=settings.LOGGING_DIR)

import json

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
        },
        'user_obj': to_user_obj(user)
    })

def tojson(obj, cb):
    try:
        jsonstr = json.dumps(obj, separators=(',', ':'))
    except:
        jsonstr = '{}'
    if cb is None:
        return jsonstr
    return "%s(%s)" % (cb, jsonstr)

class JSONPError(Exception):
    def __init__(self, errno=500):
        self.errno = errno

def return_jsonp(func):
    def _func(request, *args, **kwargs):
        if request.method == 'GET':
            cb = request.GET.get("jscallback", None)
        elif request.method == 'POST':
            cb = request.POST.get("jscallback", None)
        else:
            cb = None
        try:
            return HttpResponse(tojson(func(request, *args, **kwargs), cb),
                                content_type="application/json")
        except JSONPError as jsonp_err:
            return HttpResponse(tojson(None, cb), status=jsonp_err.errno,
                                content_type="application/json")
        except:
            print_except()
            return HttpResponse(tojson(None, cb), status=500,
                                content_type="application/json")
    _func.__name__ = func.__name__
    return _func

def arg_deco(func):
    def _func(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return func(args[0])
        def _deco(__func):
            return func(__func, *args, **kwargs)
        return _deco
    _func.__name__ = func.__name__
    return _func

@arg_deco
def auth_jsonp(func, *perms, **_kw):
    log = _kw.get('log', True)
    def _func(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            raise JSONPError(401)
        log_obj = {
            'arg': args,
            'kw': kwargs,
            'GET': request.GET,
            'a': func.__name__,
            'u': user.username,
        }
        for perm in perms:
            if not user.has_perm(perm):
                if log:
                    auth_logger.error(**log_obj)
                raise JSONPError(403)
        if log:
            auth_logger.info(**log_obj)
        return func(request, *args, **kwargs)
    _func.__name__ = func.__name__
    return _func

@return_jsonp
@auth_jsonp('oven_control.set_controller')
def add_controller(request):
    ctrl = oven_models.add_controller(
        request.GET['name'], request.GET['addr'], request.GET['port'],
        request.GET['number'], **dict((key, request.GET[key])
                                      for key in ('order', 'default_temp')))
    return {
        'id': ctrl.id,
        'name': ctrl.name,
    }

@return_jsonp
@auth_jsonp(log=False)
def get_controller_setting(request, cid=None):
    ctrl = oven_models.get_controller(cid)
    return dict((key, getattr(ctrl, key))
                for key in ('id', 'name', 'addr', 'port', 'number', 'order',
                            'default_temp'))

@return_jsonp
@auth_jsonp('oven_control.set_controller')
def set_controller(request, cid=None):
    ctrl = oven_models.get_controller(cid)
    for key in ('name', 'addr', 'port', 'number', 'order', 'default_temp'):
        if key in request.GET:
            setattr(ctrl, key, request.GET[key])
    ctrl.save()
    return {
        'id': ctrl.id,
        'name': ctrl.name,
    }

@return_jsonp
@auth_jsonp('oven_control.set_controller')
def del_controller(request, cid=None):
    return oven_models.remove_controller(cid)

@return_jsonp
def get_profiles(request):
    return [{'id': profile.id,
             'name': profile.name,
             'temps': oven_models.get_profile_temps(profile)}
             for profile in oven_models.get_profiles()]

@return_jsonp
def get_ovens(request):
    return [{'id': controller.id,
             'name': controller.name}
             for controller in oven_models.get_controllers()]

@return_jsonp
@auth_jsonp('oven_control.set_profile_temp')
def edit_profile(request, profile=None, name=None, order=None):
    profile = oven_models.get_profile(profile)
    if name:
        profile.name = name
    if order is not None:
        profile.order = order
    profile.save()
    oven_models.set_profile_temps(profile, request.GET, True)
    return {
        'id': profile.id,
        'name': profile.name
    }

@return_jsonp
@auth_jsonp('oven_control.set_profile_temp')
def add_profile(request, name=None, **kwargs):
    profile = oven_models.add_profile(name, **kwargs)
    oven_models.set_profile_temps(profile, request.GET, True)
    return {
        'id': profile.id,
        'name': profile.name
    }

@return_jsonp
@auth_jsonp(log=False)
def get_profile_setting(request, pid=None):
    profile = oven_models.get_profile(pid)
    return {
        'id': profile.id,
        'name': profile.name,
        'order': profile.order,
        'temps': oven_models.get_profile_temps(profile, False)
    }

@return_jsonp
@auth_jsonp('oven_control.set_profile_temp')
def del_profile(request, pid=None):
    return oven_models.remove_profile(pid)

@return_jsonp
def get_temps(request):
    return oven_models.controller_manager.get_temps()

@return_jsonp
@auth_jsonp('oven_control.set_temp')
def set_temps(request):
    return oven_models.controller_manager.set_temps(request.GET)

@return_jsonp
@auth_jsonp('oven_control.set_profile')
def set_profile(request, profile=None):
    res = oven_models.controller_manager.set_profile(profile)
    if not res:
        raise JSONPError(400)
    return res

@return_jsonp
def get_setpoint(request):
    return oven_models.controller_manager.get_setpoint()

@return_jsonp
@auth_jsonp(log=False)
def get_ctrl_errors(request):
    return oven_models.controller_manager.get_errors()

@return_jsonp
@auth_jsonp(log=False)
def get_auth_logs(request):
    max_count = 1000
    GET = request.GET
    logs = auth_logger.get_records(GET.get('from'), GET.get('to'),
                                   max_count + 1)
    if len(logs) > max_count:
        return {
            'logs': logs[:max_count],
            'is_all': False
        }
    return {
        'logs': logs,
        'is_all': True
    }

@return_jsonp
@auth_jsonp(log=False)
def get_ctrl_logs(request):
    max_count = 1000
    GET = request.GET
    logs = ctrl_logger.get_records(GET.get('from'), GET.get('to'),
                                   max_count + 1)
    if len(logs) > max_count:
        return {
            'logs': logs[:max_count],
            'is_all': False
        }
    return {
        'logs': logs,
        'is_all': True
    }
