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
import __main__

def run_no_sync(func, *args, **kwargs):
    if not getattr(__main__, '_django_syncdb', False):
        return func(*args, **kwargs)

class RefParent:
    def __init__(self, parent):
        self.__parent = weakref.ref(parent)
    @property
    def parent(self):
        return self.__parent()
