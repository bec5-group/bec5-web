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
from threading import Lock
from .print_color import printg, printr, printb, print_stack, print_except

import __main__

debug = bool(os.environ.get("BEC5_DEBUG", ''))

def run_no_sync(func, *args, **kwargs):
    if not getattr(__main__, '_becv_syncdb', False):
        return func(*args, **kwargs)

class RefParent:
    def __init__(self, parent):
        self.__parent = weakref.ref(parent)
    @property
    def parent(self):
        return self.__parent()

class WithLock:
    def __init__(self):
        self.__lock = Lock()
    @property
    def lock(self):
        return self.__lock
    @classmethod
    def with_lock(cls, func):
        def _func(self, *args, **kwargs):
            with self.__lock:
                return func(self, *args, **kwargs)
        _func.__name__ = func.__name__
        return _func

class _Ready:
    __cb = []
    __ready = False
    __lock = Lock()
    @classmethod
    def register(cls, func, *args, **kwargs):
        with cls.__lock:
            if not cls.__ready:
                cls.__cb.append((func, args, kwargs))
                return
        try:
            func(*args, **kwargs)
        except:
            print_except()
    @classmethod
    def _call(cls):
        with cls.__lock:
            if cls.__ready:
                return
            cls.__ready = True
        for func, args, kwargs in cls.__cb:
            try:
                func(*args, **kwargs)
            except:
                print_except()
        cls.__cb.clear()

call_when_ready = _Ready.register

class InitWhenReady:
    def __init__(self):
        call_when_ready(self.__ready_cb)
    def __ready_cb(self):
        self.init()
    def init(self):
        pass
