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

import weakref
import threading
import dbus.service
import json

from becv_utils import print_except, printb, printr, printg
from .utils import BEC5DBusFmtObj, BEC5DBusObj

class BEC5Logger(BEC5DBusFmtObj):
    __logger_count = 0
    __lock = threading.Lock()
    obj_path_fmt = '/org/yyc_arch/becv/logger/%d'
    __objs = {}
    @classmethod
    def get(cls, conn, logger):
        logger_id = id(logger)
        if logger_id not in cls.__objs:
            cls.__objs[logger_id] = cls(conn, logger)
        return cls.__objs[logger_id]
    @staticmethod
    def __new_id():
        with BEC5Logger.__lock:
            BEC5Logger.__logger_count += 1
            return BEC5Logger.__logger_count
    @property
    def logger(self):
        return self.__logger()
    def __init__(self, conn, logger):
        self.__logger = weakref.ref(logger)
        self.__logger_id = id(logger)
        BEC5DBusFmtObj.__init__(self, conn, self.__new_id())
        logger.weak_ref(self.__logger_destroied)
        logger.connect('finished', self.__logger_destroied)
    def __logger_destroied(self, *args):
        del self.__objs[self.__logger_id]
        self.remove_from_connection()
    # May looks stupid to use json here but I'm too lazy to figure out how to
    # make python-dbus does the right packaging. Also the json format is pretty
    # efficient, at least better than pickle for types that it can handle.
    @BEC5DBusObj.method("org.yyc_arch.becv.logger", threaded=True,
                        in_signature="ddi", out_signature="s", error_ret='')
    def get_records(self, _from, to, max_count):
        return json.dumps(self.__logger().get_records(_from, to, max_count),
                          separators=(',', ':'))

class BEC5DataLogger(BEC5Logger):
    @BEC5DBusObj.method("org.yyc_arch.becv.logger", threaded=True,
                        in_signature="ddi", out_signature="a(id)", error_ret=())
    def get_range(self, _from, to, max_count):
        return self.logger.get_range(_from, to, max_count)
