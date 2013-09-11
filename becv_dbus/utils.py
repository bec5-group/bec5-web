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
import dbus.service

class BEC5DBusObj(dbus.service.Object):
    obj_path = '/org/yyc_arch/becv'
    def __init__(self, mgr):
        self.__mgr = weakref.ref(mgr)
        dbus.service.Object.__init__(self, mgr.conn, self.obj_path)
    @property
    def manager(self):
        return self.__mgr()
