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

from __future__ import print_function
from django.db import models
from threading import Lock

class ControllerServer(models.Model):
    name = models.CharField(unique=True, max_length=1000)
    addr = models.CharField(max_length=1000)
    port = models.PositiveIntegerField()
    order = models.FloatField(default=0.0)
    class Meta:
        ordering = ['order', 'name']
        permissions = (
            ('edit_server', "Can add/remove/edit room temperature devices."),
        )

class ControllerDevice(models.Model):
    server = models.ForeignKey(ControllerServer)
    name = models.CharField(max_length=1000)
    unit = models.CharField(max_length=1000)
    order = models.FloatField(default=0.0)
    class Meta:
        ordering = ['order', 'name']

__room_temp_model_lock = Lock()

def with_room_temp_lock(func):
    def _func(*args, **kwargs):
        with __room_temp_model_lock:
            return func(*args, **kwargs)
    _func.no_lock = func
    return _func

@with_room_temp_lock
def add_server(name, addr, port, **kw):
    return ControllerServer.objects.create(name=name, addr=addr,
                                           port=port, **kw)

@with_room_temp_lock
def get_servers():
    return ControllerServer.objects.all()

@with_room_temp_lock
def get_server(server):
    if not isinstance(server, ControllerServer):
        return ControllerServer.objects.get(id=server)
    return server

@with_room_temp_lock
def remove_server(server):
    try:
        server = get_server.no_lock(server)
    except:
        return False
    server.delete()
    return True

@with_room_temp_lock
def server_get_devices(server):
    try:
        server = get_server.no_lock(server)
    except:
        return False
    return ControllerDevice.objects.filter(server=server)

@with_room_temp_lock
def add_device(server, name, **kw):
    return ControllerDevice.objects.create(server=get_server.no_lock(server),
                                           name=name, **kw)

@with_room_temp_lock
def get_devices():
    return ControllerDevice.objects.all()

@with_room_temp_lock
def get_device(device):
    if not isinstance(device, ControllerDevice):
        return ControllerDevice.objects.get(id=device)
    return device

@with_room_temp_lock
def remove_device(device):
    try:
        device = get_device.no_lock(device)
    except:
        return False
    device.delete()
    return True
