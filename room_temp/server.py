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

from . import utils
import time
import weakref

from becv_utils import printr, printg, printy, printb
from becv_utils.thread_helper import WithHelper, repeat_call
from logger.error_logger import ErrorLogger
from django.conf import settings
from logger import TimeLogger

server_logger = TimeLogger(filename_fmt='room_temp_actoin-%Y-%m-%d.json',
                           dirname=settings.LOGGING_DIR)

class RoomTempServer(WithHelper, ErrorLogger):
    def server_cmd(cmd_func):
        def cmd_method(self, *args, **kwargs):
            res = cmd_func(self.__addr, *args, **kwargs)
            if res is None:
                printr(cmd_func.__name__, self.__addr, args, res)
            else:
                printg(cmd_func.__name__, self.__addr, args, res)
            return res
        cmd_method.__name__ = cmd_func.__name__
        return cmd_method
    query_value = server_cmd(utils.query_value)
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
        value = repeat_call(self.query_value, (dev.name,), n=3, wait_time=0.1)
        if value is not None:
            self.clear_error(dev.name)
        else:
            self.set_error(dev.name,
                           'Get device value failed.')
        return value
    def __update_values(self):
        from . import models
        devs = models.server_get_devices(self.mgr.server)
        values = dict((dev.id, self.__get_dev_value(dev)) for dev in devs)
        # TODO
        self.mgr.set_values(values)
    def run(self):
        self.__update_values()
