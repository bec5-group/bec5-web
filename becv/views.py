from __future__ import print_function, division

from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
from django.contrib.auth import views as auth_views

import oven_control.models as oven_models

import json

def _print_with_style(prefix, suffix, *arg, **kwarg):
    end = '\n'
    if 'end' in kwarg:
        end = kwarg['end']
    kwarg['end'] = ''
    print(prefix, end='')
    print(*arg, **kwarg)
    print(suffix, end=end)

def printr(*arg, **kwarg):
    _print_with_style('\033[31;1m', '\033[0m', *arg, **kwarg)

def printg(*arg, **kwarg):
    _print_with_style('\033[32;1m', '\033[0m', *arg, **kwarg)

def printy(*arg, **kwarg):
    _print_with_style('\033[33;1m', '\033[0m', *arg, **kwarg)

def printb(*arg, **kwarg):
    _print_with_style('\033[34;1m', '\033[0m', *arg, **kwarg)

def printp(*arg, **kwarg):
    _print_with_style('\033[35;1m', '\033[0m', *arg, **kwarg)

def printbg(*arg, **kwarg):
    _print_with_style('\033[36;1m', '\033[0m', *arg, **kwarg)

import traceback
def print_except():
    try:
        printr(traceback.format_exc())
    except:
        pass

def print_stack():
    try:
        printg(''.join(traceback.format_stack()[:-1]))
    except:
        pass


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
            'oven-setcontroller': user.has_perm('oven_control.set_controller')
        },
        'user_obj': to_user_obj(user)
    })

def tojson(obj, cb):
    try:
        jsonstr = json.dumps(obj)
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
    return _func

def arg_deco(func):
    def _func(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return func(args[0])
        def _deco(__func):
            return func(__func, *args, **kwargs)
        return _deco
    return _func

@arg_deco
def auth_jsonp(func, *perms):
    def _func(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            raise JSONPError(401)
        for perm in perms:
            if not user.has_perm(perm):
                raise JSONPError(403)
        return func(request, *args, **kwargs)
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
@auth_jsonp
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
@auth_jsonp
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
    return oven_models.controller_manager.set_profile(profile)

@return_jsonp
def get_setpoint(request):
    return oven_models.controller_manager.get_setpoint()
