from __future__ import print_function
from django.db import models
from django.db.models.signals import post_save, post_delete
from . import server
from threading import Lock
from logger import bin_logger
from django.conf import settings

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
        return ControllerServer.objects.get(id=device)
    return device

@with_room_temp_lock
def remove_server(device):
    try:
        device = get_device.no_lock(device)
    except:
        return False
    device.delete()
    return True

class ServerWrapper(object):
    def __init__(self, server):
        self.server = server
        self.__server = server.RoomTempServer((self.ctrl.addr, self.ctrl.port),
                                              self)
        self.__server.timeout = 10
        self.__values = {}
        self.__lock = threading.Lock()
    def get_errors(self):
        return self.__server.get_errors()
    def __get_dev_log_fmt(self, dev_id):
        return ('room_temp_%s_%s' % (self.server.id, dev_id)) + '-%Y-%m-%d.log'
    def set_values(self, values):
        with self.__lock:
            new_values = {}
            for dev_id, value in values.items():
                dev_id = str(dev_id)
                try:
                    v = self.__values[dev_id]
                    del self.__values[dev_id]
                except:
                    log_name_fmt = self.__get_dev_log_fmt(dev_id)
                    v = {
                        'v': value,
                        'l': bin_logger.BinDateLogger(log_name_fmt,
                                                      settings.DATA_LOG_DIR,
                                                      '<Qd')
                    }
                new_values[dev_id] = v
                if value is None:
                    continue
                v['v'] = value
                v['l'].info(value)
            for dev_id, v in self.__values.items():
                v['l'].close()
            self.__values = new_values
    def get_values(self):
        with self.__lock:
            return dict((dev_id, v['v'])
                        for (dev_id, v) in self.__values.items())
    def get_value(self, dev_id):
        with self.__lock:
            return self.__values[dev_id]['v']
    def get_loggers(self):
        with self.__lock:
            return dict((dev_id, v['l'])
                        for (dev_id, v) in self.__values.items())
    def get_logger(self, dev_id):
        with self.__lock:
            return self.__values[dev_id]['l']
    def remove(self):
        self.__server.stop()
        with self.__lock:
            for dev_id, v in self.__values.items():
                try:
                    v['l'].close()
                except:
                    pass

class ServerManager(object):
    def __init__(self):
        self.__servers = {}
        self.__update_server_list()
        post_save.connect(self.__post_save_cb, sender=ControllerServer)
        post_delete.connect(self.__post_del_cb, sender=ControllerServer)
    def __post_save_cb(self, sender, **kwargs):
        self.__update_server_list()
    def __post_del_cb(self, sender, **kwargs):
        self.__update_server_list()
    def __update_server_list(self):
        servers = {}
        for server in get_servers.no_lock():
            sid = str(server.id)
            try:
                servers[sid] = self.__servers[sid]
                servers[sid].server = server
                del self.__servers[sid]
            except:
                servers[sid] = ServerWrapper(server)
        for sid, server in self.__servers.items():
            self.__servers[sid].remove()
            del self.__servers[sid]
        self.__servers = servers
    def get_errors(self):
        errors = {}
        for sid, server in self.__servers.items():
            server_errors = server.get_errors()
            if server_errors:
                errors[sid] = {'name': server.server.name,
                               'errors': server_errors}
        return errors
    def get_values(self):
        return dict((sid, server.get_values()) for (sid, server)
                    in self.__servers.items())
    def get_loggers(self):
        return dict((sid, server.get_loggers()) for (sid, server)
                    in self.__servers.items())

if not getattr(__import__('__main__'), '_django_syncdb', False):
    server_manager = ServerManager()
