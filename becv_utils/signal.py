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

from django.dispatch import Signal

class SignalWrapper(object):
    def __init__(self, signal, obj):
        self.__signal = signal
        self.__obj = obj
    def __getattr__(self, key):
        val = getattr(self.__signal, key)
        if key in ('connect', 'disconnect', 'has_listener'):
            def func(*args, **kwargs):
                if not 'sender' in kwargs:
                    kwargs['sender'] = self.__obj
                return val(*args, **kwargs)
            return func
        if key in ('send', 'send_robust'):
            def func(*args, **kwargs):
                if len(args) == 0:
                    args = (self.__obj,)
                return val(*args, **kwargs)
            return func
        return val

class ObjSignal(Signal):
    def __init__(self, *args, **kwargs):
        Signal.__init__(self, *args, **kwargs)
    def __get__(self, obj, owner):
        if obj is None:
            return self
        return SignalWrapper(self, obj)

def bind_signal(src, dst):
    def _resender(sender=None, signal=None, **kwargs):
        dst.send_robust(**kwargs)
    src.connect(_resender)
    return _resender
