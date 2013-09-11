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
import decorator
import inspect
import dbus.service
from becv_utils import print_except, printb, printr, printg

class BEC5DBusObj(dbus.service.Object):
    obj_path = '/org/yyc_arch/becv'
    def __init__(self, mgr):
        self.__mgr = weakref.ref(mgr)
        dbus.service.Object.__init__(self, mgr.conn, self.obj_path)
    @property
    def becv_manager(self):
        return self.__mgr()
    def __check_sender(self, sender):
        if sender is None:
            return False
        uid = self.__mgr().get_peer_uid(sender)
        if uid is None or (uid != 0 and uid != os.getuid()):
            return False
        return True
    @classmethod
    def method(cls, *a, error_ret=False, **kw):
        dbus_deco = dbus.service.method(*a, sender_keyword='_sender', **kw)
        def _deco(func):
            def _func(self, *_args, _sender=None):
                if not self.__check_sender(_sender):
                    return error_ret
                try:
                    return func(self, *_args)
                except:
                    print_except()
                    return error_ret
            eval_dict = {'_func': _func}
            args = ', '.join(inspect.getfullargspec(func)[0])
            name = func.__name__
            _func = decorator.FunctionMaker.create(
                '%s(%s, _sender=None)' % (name, args),
                'return _func(%s, _sender=_sender)' % args, eval_dict)
            return dbus_deco(_func)
        return _deco

class BEC5DBusFmtObj(BEC5DBusObj):
    obj_path_fmt = '/org/yyc_arch/becv/%d'
    def __init__(self, mgr, *args):
        self.obj_path = self.obj_path_fmt % args
        BEC5DBusObj.__init__(self, mgr)
