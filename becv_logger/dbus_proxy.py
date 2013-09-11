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

class DBusLoggerProxy:
    def __init__(self, path):
        self.__logger_obj = sys_mgr.get_object('org.yyc_arch.becv', path)
        self.__logger = self.__logger_obj.get_iface(
            'org.yyc_arch.becv.logger')
    def get_records(self, _from, to=None, max_count=None):
        if to is None:
            to = -1
        if max_count is None:
            max_count = -1
        return json.loads(self.__logger.get_records(_from, to, max_count))
    def get_range(self, _from, to=None, max_count=None):
        if to is None:
            to = -1
        if max_count is None:
            max_count = -1
        return self.__logger.get_range(_from, to, max_count)
