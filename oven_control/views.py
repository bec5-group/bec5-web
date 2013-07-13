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

from json_view import JSONPError, return_jsonp, auth_jsonp
from . import models
from .controller import ctrl_logger
import time

@return_jsonp
def get_ovens(request):
    return [{'id': controller.id,
             'name': controller.name}
             for controller in models.get_controllers()]

@return_jsonp
@auth_jsonp
def get_controller_setting(request, cid=None):
    ctrl = models.get_controller(cid)
    return dict((key, getattr(ctrl, key))
                for key in ('id', 'name', 'addr', 'port', 'number', 'order',
                            'default_temp'))

def _add_controller_logger(request):
    GET = request.GET.get
    return ('Name: %s, Address: %s:%s, NO: %s, Order: %s, '
            'Default Temperature: %s' %
            (GET('name'), GET('addr'), GET('port'), GET('number'),
             GET('order'), GET('default_temp')))

@return_jsonp
@auth_jsonp('oven_control.set_controller', log=_add_controller_logger)
def add_controller(request):
    ctrl = models.add_controller(
        request.GET['name'], request.GET['addr'], request.GET['port'],
        request.GET['number'], **dict((key, request.GET[key])
                                      for key in ('order', 'default_temp')))
    return {
        'id': ctrl.id,
        'name': ctrl.name,
    }

def _set_controller_logger(request, cid=None):
    GET = request.GET.get
    ctrl = models.get_controller(cid)
    old_name = ctrl.name
    name = GET('name')
    if name == old_name:
        return ('Name: %s, Address: %s:%s, NO: %s, Order: %s, '
                'Default Temperature: %s' %
                (name, GET('addr'), GET('port'), GET('number'),
                 GET('order'), GET('default_temp')))
    return ('Name: %s, New Name: %s, Address: %s:%s, NO: %s, Order: %s, '
            'Default Temperature: %s' %
            (old_name, name, GET('addr'), GET('port'), GET('number'),
             GET('order'), GET('default_temp')))

@return_jsonp
@auth_jsonp('oven_control.set_controller', log=_set_controller_logger)
def set_controller(request, cid=None):
    ctrl = models.get_controller(cid)
    for key in ('name', 'addr', 'port', 'number', 'order', 'default_temp'):
        if key in request.GET:
            setattr(ctrl, key, request.GET[key])
    ctrl.save()
    return {
        'id': ctrl.id,
        'name': ctrl.name,
    }

def _del_controller_logger(request, cid=None):
    ctrl = models.get_controller(cid)
    return 'Name: %s' % ctrl.name

@return_jsonp
@auth_jsonp('oven_control.set_controller', log=_del_controller_logger)
def del_controller(request, cid=None):
    return models.remove_controller(cid)

@return_jsonp
def get_profiles(request):
    return [{'id': profile.id,
             'name': profile.name,
             'temps': models.get_profile_temps(profile)}
             for profile in models.get_profiles()]

def _add_profile_logger(request, name=None, order=None):
    res = 'Name: ' + name
    if order is not None:
        res = res + ', Order: ' + order
    if len(request.GET):
        res = res + ', Temperatures: { '
        for cid, temp in request.GET.items():
            try:
                ctrl = models.get_controller(cid)
                res += ctrl.name + ': ' + temp + ', '
            except:
                pass
        res = res + '}'
    return res

@return_jsonp
@auth_jsonp('oven_control.set_profile_temp', log=_add_profile_logger)
def add_profile(request, name=None, **kwargs):
    profile = models.add_profile(name, **kwargs)
    models.set_profile_temps(profile, request.GET, True)
    return {
        'id': profile.id,
        'name': profile.name
    }

@return_jsonp
@auth_jsonp
def get_profile_setting(request, pid=None):
    profile = models.get_profile(pid)
    return {
        'id': profile.id,
        'name': profile.name,
        'order': profile.order,
        'temps': models.get_profile_temps(profile, False)
    }

def _edit_profile_logger(request, profile=None, name=None, order=None):
    profile = models.get_profile(profile)
    res = 'Name: ' + profile.name
    if name and name != profile.name:
        res = res + ', New Name: ' + name
    if order is not None:
        res = res + ', Order: ' + order
    if len(request.GET):
        res = res + ', Temperatures: { '
        for cid, temp in request.GET.items():
            try:
                ctrl = models.get_controller(cid)
                res += ctrl.name + ': ' + temp + ', '
            except:
                pass
        res = res + '}'
    return res

@return_jsonp
@auth_jsonp('oven_control.set_profile_temp', log=_edit_profile_logger)
def edit_profile(request, profile=None, name=None, order=None):
    profile = models.get_profile(profile)
    if name:
        profile.name = name
    if order is not None:
        profile.order = order
    profile.save()
    models.set_profile_temps(profile, request.GET, True)
    return {
        'id': profile.id,
        'name': profile.name
    }

def _del_profile_logger(request, pid=None):
    profile = models.get_profile(pid)
    return 'Name: ' + profile.name

@return_jsonp
@auth_jsonp('oven_control.set_profile_temp', log=_del_profile_logger)
def del_profile(request, pid=None):
    return models.remove_profile(pid)

@return_jsonp
def get_temps(request):
    return models.controller_manager.get_temps()

@return_jsonp
def get_setpoint(request):
    return models.controller_manager.get_setpoint()

def _set_profile_logger(request, profile=None):
    profile = models.get_profile(profile)
    return 'Name: ' + profile.name

@return_jsonp
@auth_jsonp('oven_control.set_profile', log=_set_profile_logger)
def set_profile(request, profile=None):
    res = models.controller_manager.set_profile(profile)
    if not res:
        raise JSONPError(400)
    return res

def _set_temps_logger(request):
    res = ''
    for cid, temp in request.GET.items():
        try:
            ctrl = models.get_controller(cid)
            res += ctrl.name + ': ' + temp + ', '
        except:
            pass
    return res

@return_jsonp
@auth_jsonp('oven_control.set_temp', log=_set_temps_logger)
def set_temps(request):
    return models.controller_manager.set_temps(request.GET)

@return_jsonp
@auth_jsonp
def get_errors(request):
    return models.controller_manager.get_errors()

@return_jsonp
@auth_jsonp
def get_logs(request):
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

@return_jsonp
@auth_jsonp
def get_temp_logs(request):
    max_count = 1000
    GET = request.GET
    loggers = models.controller_manager.get_loggers()
    try:
        _to = int(float(GET['to']))
    except:
        _to = time.time()
    _from = max(int(float(GET['from'])), _to - 31622400) # one year
    return dict((ctrl, loggers[int(ctrl)].get_range(_from, _to, max_count))
                for ctrl in GET.getlist('ctrl[]'))
