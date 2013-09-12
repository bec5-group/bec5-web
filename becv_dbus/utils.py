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
import weakref
import decorator
import inspect
import dbus.service
import threading
from gi.repository import GLib
from becv_utils import print_except, printb, printr, printg

class BEC5DBusObj(dbus.service.Object):
    obj_path = '/org/yyc_arch/becv'
    def __init__(self, mgr):
        self.__mgr = weakref.ref(mgr)
        dbus.service.Object.__init__(self, mgr.conn, self.obj_path)
    @property
    def becv_manager(self):
        return self.__mgr()
    @classmethod
    def method(cls, *a, error_ret=False, threaded=False, **kw):
        if threaded:
            dbus_deco = dbus.service.method(*a, async_callbacks=('_reply_hdl',
                                                                 '_error_hdl'),
                                            **kw)
        else:
            dbus_deco = dbus.service.method(*a, **kw)
        def _deco(func):
            if threaded:
                def _func(self, *_args, _reply_hdl=None, _error_hdl=None):
                    def __worker():
                        try:
                            res = func(self, *_args)
                        except:
                            print_except()
                            res = error_ret
                        ctx = GLib.main_context_default()
                        ctx.invoke_full(0, _reply_hdl, res)
                    thread = threading.Thread(target=__worker, daemon=True)
                    thread.start()
                func_fmt = ('%s(%s, _reply_hdl=None, _error_hdl=None)')
                func_fmt2 = ('_func(%s, _reply_hdl=_reply_hdl, '
                             '_error_hdl=_error_hdl)')
            else:
                def _func(self, *_args):
                    try:
                        return func(self, *_args)
                    except:
                        print_except()
                        return error_ret
                func_fmt = '%s(%s)'
                func_fmt2 = '_func(%s)'
            eval_dict = {'_func': _func}
            args_sig = ', '.join(inspect.getfullargspec(func)[0])
            name = func.__name__
            _func = decorator.FunctionMaker.create(
                func_fmt % (name, args_sig),
                'return ' + func_fmt2 % args_sig, eval_dict)
            return dbus_deco(_func)
        return _deco

class BEC5DBusFmtObj(BEC5DBusObj):
    obj_path_fmt = '/org/yyc_arch/becv/%d'
    def __init__(self, mgr, *args):
        self.obj_path = self.obj_path_fmt % args
        BEC5DBusObj.__init__(self, mgr)
