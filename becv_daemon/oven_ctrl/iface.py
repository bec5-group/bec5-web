#   Copyright (C) 2013~2014 by Yichao Yu
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

from os import path as _path

from becv_utils import print_except, printb, printr, printg
from oven_control_service.controller import ControllerManager
from becv_dbus import BEC5DBusObj, BEC5DBusFmtObj
from ..logger import BEC5Logger, BEC5DataLogger
from becv_utils.math import fix_non_finite
from . import db

class BEC5OvenController(BEC5DBusFmtObj):
    obj_path_fmt = '/org/yyc_arch/becv/oven_control/%s'
    def __init__(self, conn, ctrl):
        self.__ctrl = ctrl
        BEC5DBusFmtObj.__init__(self, conn, ctrl.id)
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="s", error_ret='')
    def get_id(self):
        return self.__ctrl.id
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="s", error_ret='')
    def get_name(self):
        return self.__ctrl.name
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="(si)",
                        error_ret=('', -1))
    def get_addr(self):
        return self.__ctrl.addr
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="s", error_ret='')
    def get_url(self):
        return self.__ctrl.url
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="i", error_ret=-1)
    def get_port(self):
        return self.__ctrl.port
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="i", error_ret=-1)
    def get_dev_no(self):
        return self.__ctrl.dev_no
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="d", error_ret=0.0)
    def get_temp(self):
        return fix_non_finite(self.__ctrl.temp)
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="d", error_ret=0.0)
    def get_set_temp(self):
        return fix_non_finite(self.__ctrl.set_temp)
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="d", error_ret=0.0)
    def get_real_set_temp(self):
        return fix_non_finite(self.__ctrl.real_set_temp)
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="d", out_signature="b")
    def set_temp(self, value):
        self.__ctrl.set_temp = value
        return True
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="o", error_ret=None)
    def get_data_logger(self):
        return BEC5DataLogger.get(self.becv_manager, self.__ctrl.data_logger)
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="aa{ss}")
    def get_errors(self):
        return self.__ctrl.get_errors()

class BEC5OvenControlManager(BEC5DBusObj):
    obj_path = '/org/yyc_arch/becv/oven_control'
    def __init__(self, conn):
        BEC5DBusObj.__init__(self, conn)
        self.__manager = ControllerManager()
        self.__ctrl_objs = {}
        self.__manager.connect('dev-added', self.__on_dev_added)
        self.__manager.connect('dev-removed', self.__on_dev_removed)
    def __on_dev_added(self, mgr, cid):
        self.__ctrl_objs[cid] = BEC5OvenController(self.becv_manager,
                                                   self.__manager[cid])
    def __on_dev_removed(self, mgr, cid):
        self.__ctrl_objs[cid].remove_from_connection()
        del self.__ctrl_objs[cid]
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="aa{sv}", out_signature="b")
    def set_controllers(self, ctrls):
        self.__manager.set_controllers(ctrls)
        return True
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="o", error_ret=None)
    def get_logger(self):
        return BEC5Logger.get(self.becv_manager, self.__manager.logger)
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="sa{sd}", out_signature="b")
    def set_temps(self, profile, temps):
        return self.__manager.set_temps(profile, temps)
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="a{s(saa{ss})}")
    def get_errors(self):
        return self.__manager.get_errors()
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="a{sd}")
    def get_temps(self):
        return self.__manager.get_temps()
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="sa{sd}")
    def get_setpoints(self):
        return self.__manager.get_setpoints()
    @BEC5DBusObj.method("org.yyc_arch.becv.oven_control",
                        in_signature="", out_signature="a{so}")
    def get_data_loggers(self):
        return {cid: BEC5DataLogger.get(self.becv_manager, logger)
                for cid, logger in self.__manager.get_data_loggers().items()}
