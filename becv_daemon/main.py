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

import json
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from becv_logger import log_dir as _log_dir
from becv_sql import BEC5Sql

class BEC5DBusManager:
    def __init__(self, config_file):
        DBusGMainLoop(set_as_default=True)
        try:
            with open(config_file) as fh:
                self.__config = json.load(fh)
        except:
            self.__config = {}
        self.__init_db__()
        self.__init_log_dir__()
        self.__main_loop = GLib.MainLoop()
        self.__sys_bus = dbus.SystemBus()
        self.__bus_name = dbus.service.BusName('org.yyc_arch.becv',
                                               bus=self.__sys_bus)
        self.__dbus_mgr = self.__sys_bus.get_object('org.freedesktop.DBus', '/')
        self.__dbus_mgr_iface = dbus.Interface(
            self.__dbus_mgr, dbus_interface='org.freedesktop.DBus')

        # Import after database is initialized
        from .oven_ctrl import BEC5OvenControlManager
        self.__obj_mgr = BEC5OvenControlManager(self)
    def __init_db__(self):
        dbpath = self.__config.get('DB_PATH', '/srv/bec5/db/bec5-daemon.db')
        self.__sql = BEC5Sql.instance("sqlite:///" + dbpath)
    def __init_log_dir__(self):
        self.__log_dir = self.__config.get('LOG_DIR', '/srv/bec5/log')
        self.__data_log_dir = self.__config.get('DATA_LOG_DIR',
                                                '/srv/bec5/log')
        _log_dir.LOG_DIR = self.__log_dir
        _log_dir.DATA_LOG_DIR = self.__data_log_dir
    def get_peer_uid(self, sender):
        return self.__dbus_mgr_iface.GetConnectionUnixUser(sender)
    @property
    def conn(self):
        return self.__sys_bus
    def run(self):
        self.__main_loop.run()
