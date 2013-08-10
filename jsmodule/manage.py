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

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

class Script:
    @property
    def name(self):
        return self.__name
    def __init__(self, name, url='', sync_deps=(), deps=(), static=False):
        self.__name = name
        if not url:
            raise ValueError('Url of script cannot be empty.')
        self.__url = url
        self.__sync_deps = tuple(sync_deps if sync_deps else ())
        self.__deps = tuple(deps if deps else ())
        self.__static = bool(static)
    def to_obj(self):
        url = self.__url
        if self.__static:
            url = staticfiles_storage.url(url)
        return {
            'name': name,
            'url': url,
            'sync_deps': self.__sync_deps,
            'deps': self.__deps,
        }

class ScriptManager:
    script_class = Script
    def __init__(self):
        self.__scripts = {}
    def register(self, name, **info):
        if name in self.__scripts:
            raise ValueError("Script %s already registered." % name)
        self.__scripts = self.script_class(name, **info)
    def get_info(self):
        return dict((name, script.to_obj()) for (name, script)
                    in self.__scripts.items())

script_manager = ScriptManager()
