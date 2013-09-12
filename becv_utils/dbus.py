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
import dbus

from .misc import WithLock
from .print_color import printb, printg, printr

class DBusMethod(WithLock):
    def __init__(self, iface, name):
        WithLock.__init__(self)
        self.__iface = iface
        self.__name = name
    @property
    @WithLock.with_lock
    def method(self):
        return getattr(self.__iface.iface, self.__name)
    def __call__(self, *args):
        return self.method(*args, timeout=60)

class DBusIFace(WithLock):
    def __init__(self, obj, name):
        WithLock.__init__(self)
        self.__obj = obj
        self.__name = name
    def __getattr__(self, name):
        return DBusMethod(self, name)
    @property
    @WithLock.with_lock
    def iface(self):
        return dbus.Interface(self.__obj.obj, dbus_interface=self.__name)

class DBusObject(WithLock):
    def __init__(self, mgr, name, path):
        WithLock.__init__(self)
        self.__mgr = mgr
        self.__name = name
        self.__path = path
    def get_iface(self, name):
        return DBusIFace(self, name)
    @property
    def conn(self):
        return self.__mgr.conn
    @property
    @WithLock.with_lock
    def obj(self):
        return self.__mgr.conn.get_object(self.__name, self.__path)

class SysConnMgr(WithLock):
    __conn = None
    def __init__(self):
        WithLock.__init__(self)
        self.__conn = None
        self.__pid = None
    def get_object(self, name, path):
        return DBusObject(self, name, path)
    @property
    @WithLock.with_lock
    def conn(self):
        if self.__conn is not None:
            if self.__pid == os.getpid():
                return self.__conn
            try:
                self.__conn.close()
                del self.__conn
            except:
                pass
        self.__conn = dbus.SystemBus()
        self.__pid = os.getpid()
        return self.__conn

sys_mgr = SysConnMgr()
