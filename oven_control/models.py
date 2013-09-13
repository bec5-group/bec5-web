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

from django.db import models
from threading import Lock
import json

from becv_utils.math import to_finite

class TempController(models.Model):
    name = models.CharField(unique=True, max_length=1000)
    addr = models.CharField(max_length=1000)
    port = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    order = models.FloatField(default=0.0)
    default_temp = models.FloatField(default=0.0)
    class Meta:
        ordering = ['order', 'default_temp', 'name']
        permissions = (
            ('set_temp', "Can set controller temperatures."),
            ('set_controller', "Can change controller setting.")
        )
    def __str__(self):
        return json.dumps({k: getattr(self, k)
                           for k in ('name', 'addr', 'port', 'number',
                                     'order', 'default_temp')}, indent=2)

class TempProfile(models.Model):
    name = models.CharField(unique=True, max_length=1000)
    order = models.FloatField(default=0.0)
    class Meta:
        ordering = ['order', 'name']
        permissions = (
            ('set_profile', "Can change profile."),
            ('set_profile_temp', "Can change profile setting.")
        )
    def __str__(self):
        return json.dumps({k: getattr(self, k)
                           for k in ('name', 'order')}, indent=2)

class TempSetPoint(models.Model):
    control = models.ForeignKey(TempController)
    temperature = models.FloatField(default=0.0)
    profile = models.ForeignKey(TempProfile)
    class Meta:
        ordering = ['control__order', 'control__default_temp', 'control__name']

__oven_control_model_lock = Lock()

def with_oven_control_lock(func):
    def _func(*args, **kwargs):
        with __oven_control_model_lock:
            return func(*args, **kwargs)
    _func.no_lock = func
    return _func

@with_oven_control_lock
def add_controller(name, addr, port, number, **kw):
    return TempController.objects.create(name=name, addr=addr, port=port,
                                         number=number, **kw)

@with_oven_control_lock
def get_controllers():
    return TempController.objects.all()

@with_oven_control_lock
def get_controller(cid):
    return TempController.objects.get(id=cid)

@with_oven_control_lock
def remove_controller(controller):
    try:
        if not isinstance(controller, TempController):
            controller = get_controller.no_lock(controller)
    except:
        return False
    controller.delete()
    return True


@with_oven_control_lock
def get_profiles():
    return TempProfile.objects.all()

@with_oven_control_lock
def get_profile(pid):
    return TempProfile.objects.get(id=pid)

@with_oven_control_lock
def get_profile_temps(profile, use_default=True):
    if not isinstance(profile, TempProfile):
        profile = get_profile.no_lock(profile)
    set_points = TempSetPoint.objects.filter(profile=profile)
    temps = {}
    for controller in get_controllers.no_lock():
        cid = controller.id
        try:
            temps[cid] = set_points.get(control=controller).temperature
        except:
            if use_default:
                temps[cid] = controller.default_temp
    return temps

@with_oven_control_lock
def add_profile(name, **kw):
    return TempProfile.objects.create(name=name, **kw)

@with_oven_control_lock
def set_profile_temps(profile, temps, ignore_error=True):
    if not isinstance(profile, TempProfile):
        profile = get_profile.no_lock(profile)
    temp_sets = []
    for cid, temp in temps.items():
        try:
            controller = get_controller.no_lock(cid)
            temp = to_finite(temp)
        except:
            if not ignore_error:
                return False
            continue
        temp_sets.append((controller, temp))
    for controller, temp in temp_sets:
        TempSetPoint.objects.filter(control=controller,
                                    profile=profile).delete()
        TempSetPoint.objects.create(control=controller,
                                    profile=profile,
                                    temperature=temp)
    return True

@with_oven_control_lock
def remove_profile(profile):
    try:
        if not isinstance(profile, TempProfile):
            profile = get_profile.no_lock(profile)
    except:
        return False
    profile.delete()
    return True
