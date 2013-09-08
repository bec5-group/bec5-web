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
import threading
from . import print_except
from .misc import RefParent
from time import sleep

def repeat_call(func, args=(), kwargs={}, n=1, wait_time=0, wait_first=True):
    res = None
    for i in range(n):
        if (i or wait_first) and wait_time > 0:
            sleep(wait_time)
        res = func(*args, **kwargs)
        if res is not None:
            break
    return res

# Run parent's .run() periodically or when activated in a separate thread.
class ThreadHelper(RefParent):
    def __init__(self, parent):
        RefParent.__init__(self, parent)
        self.__event = threading.Event()
        self.__thread = threading.Thread(target=self.__run, daemon=True)
        self.__timeout = 1
        self.__running = False
    def activate(self):
        self.__event.set()
    @property
    def timeout(self):
        return self.__timeout
    @timeout.setter
    def timeout(self, value):
        if not value or value <= 0:
            value = None
        self.__timeout = value
    def start(self):
        self.__running = True
        self.__thread.start()
    def stop(self):
        self.__running = False
        self.activate()
    def __run_iter(self):
        parent = self.parent
        if parent is None:
            self.__running = False
            return False
        try:
            parent.run()
        except:
            print_except()
        return True
    def __run(self):
        while self.__running:
            self.__event.wait(self.timeout)
            self.__event.clear()
            if not self.__run_iter():
                break

# class that uses ThreadHelper
class WithHelper:
    def __init__(self):
        self.__helper = ThreadHelper(self)
    def run(self):
        pass
    def activate(self):
        return self.__helper.activate()
    def start(self):
        return self.__helper.start()
    def stop(self):
        return self.__helper.stop()
    @property
    def timeout(self):
        return self.__helper.timeout
    @timeout.setter
    def timeout(self, value):
        old_value = self.__helper.timeout
        self.__helper.timeout = value
        if value != old_value:
            self.activate()
    def __del__(self):
        self.stop()
