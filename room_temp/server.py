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

import os
import time
import weakref
import threading

from django.db.models.signals import post_save, post_delete
from django.conf import settings

from becv_utils import printr, printg, printy, printb
from becv_utils.thread_helper import WithHelper, repeat_call
from becv_logger.error_logger import ErrorLogger
from becv_logger import TimeLogger, bin_logger

from . import utils
from . import models

server_logger = TimeLogger(filename_fmt='room_temp_action-%Y-%m-%d.json',
                           dirname=settings.LOGGING_DIR)

class RoomTempServer(WithHelper, ErrorLogger):
    def server_cmd(cmd_func):
        def cmd_method(self, *args, **kwargs):
            res = cmd_func(self.__addr, *args, **kwargs)
            if os.environ.get("BEC5_DEBUG", ''):
                if res is None:
                    printr(cmd_func.__name__, self.__addr, args, res)
                else:
                    printg(cmd_func.__name__, self.__addr, args, res)
            return res
        cmd_method.__name__ = cmd_func.__name__
        return cmd_method
    query_value = server_cmd(utils.query_value)
    enable_output = server_cmd(utils.enable_output)
    del server_cmd
    @property
    def mgr(self):
        return self.__mgr()
    def __init__(self, addr, mgr):
        WithHelper.__init__(self)
        ErrorLogger.__init__(self)
        self.__addr = addr
        self.__mgr = weakref.ref(mgr)
        self.start()
    def _error_logger_handle(self, name, is_error, msg):
        if is_error:
            server_logger.error(name=name, msg=msg, addr=self.addr,
                                server=self.mgr.server.name)
        else:
            server_logger.info(name=name, msg=msg, addr=self.addr,
                               server=self.mgr.server.name)
    def stop(self):
        WithHelper.stop(self)
        del self.__mgr
    @property
    def addr(self):
        return self.__addr
    @addr.setter
    def addr(self, addr):
        self.__addr = addr
    def __get_dev_value(self, dev):
        value = repeat_call(self.query_value, (dev.name,), n=3, wait_time=0.2)
        if value is not None:
            self.clear_error(dev.name)
        else:
            self.set_error(dev.name, 'Get device value failed.')
        return value
    def __update_values(self):
        devs = models.server_get_devices(self.mgr.server)
        values = dict((dev.id, self.__get_dev_value(dev)) for dev in devs)
        self.mgr.set_values(values)
        repeat_call(self.enable_output, n=3, wait_time=0.3)
    def run(self):
        self.__update_values()

class ServerWrapper(object):
    def __init__(self, server):
        self.server = server
        self.__server = RoomTempServer((server.addr, server.port), self)
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
                        'l': bin_logger.FloatDateLogger(log_name_fmt,
                                                        settings.DATA_LOG_DIR)
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
        post_save.connect(self.__post_save_cb, sender=models.ControllerServer)
        post_delete.connect(self.__post_del_cb, sender=models.ControllerServer)
    def __post_save_cb(self, sender, **kwargs):
        self.__update_server_list()
    def __post_del_cb(self, sender, **kwargs):
        self.__update_server_list()
    def __update_server_list(self):
        servers = {}
        for server in models.get_servers.no_lock():
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
    manager = ServerManager()
