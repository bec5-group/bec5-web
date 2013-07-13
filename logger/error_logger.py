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

import time

class ErrorLogger(object):
    def __init__(self):
        self.__errors = {}
    def _error_logger_handle(self, name, is_error, msg):
        pass
    def get_errors(self):
        return [{'name': name, 'msg': err['msg']}
                for name, err in self.__errors.items() if err['error']]
    def clear_error(self, name):
        cur_time = int(time.time())
        err_obj = self.__errors.get(name, {'time': None, 'error': False,
                                           'msg': ''})
        if err_obj['error']:
            err_obj['error'] = False
            try:
                self._error_logger_handle(name, False, 'error cleared.')
            except:
                pass
        err_obj['time'] = cur_time
        self.__errors[name] = err_obj
    def set_error(self, name, msg):
        err_obj = self.__errors.get(name, {'time': None, 'error': True,
                                           'msg': ''})
        last_t = err_obj['time']
        cur_time = int(time.time())
        if last_t is not None and (last_t > cur_time - 100 or
                                   (last_t > cur_time - 600 and
                                    err_obj['error'])):
            return
        err_obj['time'] = cur_time
        err_obj['error'] = True
        err_obj['msg'] = msg
        self.__errors[name] = err_obj
        try:
            self._error_logger_handle(name, True, msg)
        except:
            pass
