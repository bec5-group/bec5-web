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
from .utils import BEC5DBusObj

class BEC5OvenControlManager(BEC5DBusObj):
    def __init__(self, conn):
        BEC5DBusObj.__init__(self, conn)
        self.__manager = oven_manager
    @dbus.service.method("org.yyc_arch.becv.oven_control",
                         in_signature="s",
                         out_signature="b", sender_keyword='sender')
    def set_log_path(self, dirname, sender=None):
        if sender is None or not _path.isabs(dirname):
            return False
        uid = dbus.get_peer_unix_user(sender)
        if uid is None or (uid != 0 and uid != os.getuid()):
            return False
        try:
            self.__manager.set_log_path(dirname)
            return True
        except:
            return False
