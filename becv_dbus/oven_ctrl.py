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

from os import path as _path
import os
import dbus.service

from oven_control_service.controller import manager as oven_manager
from .utils import BEC5DBusObj, BEC5DBusFmtObj

class BEC5OvenController(BEC5DBusFmtObj):
    obj_path_fmt = '/org/yyc_arch/becv/oven_control/%d'
    def __init__(self, conn, ctrl):
        self.__ctrl = ctrl
        BEC5DBusFmtObj.__init__(self, conn, ctrl.id)

class BEC5OvenControlManager(BEC5DBusObj):
    obj_path = '/org/yyc_arch/becv/oven_control'
    def __init__(self, conn):
        BEC5DBusObj.__init__(self, conn)
        self.__manager = oven_manager
        self.__ctrl_objs = {}
        oven_manager.connect('dev-added', self.__on_dev_added)
        oven_manager.connect('dev-removed', self.__on_dev_removed)
    def __on_dev_added(self, mgr, cid):
        self.__ctrl_objs[cid] = BEC5OvenController(self.becv_manager,
                                                   self.__manager[cid])
    def __on_dev_removed(self):
        self.__ctrl_objs[cid].remove_from_connection()
        del self.__ctrl_objs[cid]
    def __check_sender(self, sender):
        if sender is None:
            return False
        uid = self.becv_manager.conn.get_peer_unix_user(sender)
        if uid is None or (uid != 0 and uid != os.getuid()):
            return False
        return True
    @dbus.service.method("org.yyc_arch.becv.oven_control",
                         in_signature="s",
                         out_signature="b", sender_keyword='sender')
    def set_log_path(self, dirname, sender=None):
        if not _path.isabs(dirname) or not self.__check_sender(sender):
            return False
        try:
            self.__manager.set_log_path(dirname)
            return True
        except:
            return False
    @dbus.service.method("org.yyc_arch.becv.oven_control",
                         in_signature="aa{sv}",
                         out_signature="b", sender_keyword='sender')
    def set_controllers(self, ctrls, sender=None):
        if not self.__check_sender(sender):
            return False
        try:
            self.__manager.set_controllers(ctrls)
            return True
        except:
            return False
