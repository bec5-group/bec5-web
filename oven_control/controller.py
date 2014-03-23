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

from django.db.models.signals import post_save, post_delete

from becv_utils.misc import run_no_sync, InitWhenReady
from becv_utils.dbus import sys_mgr
from becv_utils import printg, printb, printr
from becv_logger.dbus_proxy import DBusLoggerProxy

from . import models

@run_no_sync
class manager(InitWhenReady):
    def __init__(self):
        InitWhenReady.__init__(self)
        self.__oven_obj = sys_mgr.get_object(
            'org.yyc_arch.becv', '/org/yyc_arch/becv/oven_control')
        self.__oven_mgr = self.__oven_obj.get_iface(
            'org.yyc_arch.becv.oven_control')
        self.__logger = DBusLoggerProxy(self.__oven_mgr.get_logger())
    def init(self):
        self.__set_controllers()
        post_save.connect(self.__post_save_cb, sender=models.TempController)
        post_delete.connect(self.__post_del_cb, sender=models.TempController)
    @property
    def logger(self):
        return self.__logger
    def __post_save_cb(self, sender, **kwargs):
        self.__set_controllers()
    def __post_del_cb(self, sender, **kwargs):
        self.__set_controllers()
    def __set_controllers(self):
        self.__oven_mgr.set_controllers(
            [{'id': str(ctrl.id), 'name': ctrl.name, 'addr': ctrl.addr,
              'port': ctrl.port, 'number': ctrl.number}
             for ctrl in models.get_controllers()])
    def get_temps(self):
        # Not sure how to do this automatically
        return {str(cid): float(temp) for cid, temp
                in self.__oven_mgr.get_temps().items()}
    def get_setpoints(self):
        pid, temps = self.__oven_mgr.get_setpoints()
        return {
            'id': str(pid),
            'name': models.get_profile(pid).name if pid else '',
            'temps': {str(cid): float(temp) for cid, temp in temps.items()}
        }
    def __set_temps(self, profile, temps):
        self.__oven_mgr.set_temps(profile, {str(cid): temp for cid, temp
                                            in temps.items()})
        return True
    def set_profile(self, profile):
        if not profile:
            return
        return self.__set_temps(profile, models.get_profile_temps(profile))
    def set_temps(self, temps):
        return self.__set_temps('', temps)
    def get_errors(self):
        return {str(cid): {'name': str(name), 'errors': errors}
                for cid, (name, errors)
                in self.__oven_mgr.get_errors().items()}
    def get_loggers(self):
        return {str(cid): DBusLoggerProxy(log_path) for cid, log_path
                in self.__oven_mgr.get_data_loggers().items()}
