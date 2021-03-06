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

"""
Manage script dependency info.
"""

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from urllib.parse import urljoin

def static_url(url):
    return staticfiles_storage.url(url)

def _fix_deps(deps):
    if not deps:
        return ()
    elif isinstance(deps, str):
        return (deps,)
    else:
        return tuple(deps)

class Script:
    @property
    def name(self):
        return self.__name
    def __init__(self, name, url='', sync_deps=(), deps=(), static=False,
                 jsmodule=False, no_cache=False):
        self.__name = name
        if not url:
            raise ValueError('Url of script cannot be empty.')
        self.__url = url
        self.__sync_deps = _fix_deps(sync_deps)
        self.__deps = _fix_deps(deps)
        self.__static = bool(static)
        self.__jsmodule = bool(jsmodule)
        self.__no_cache = bool(no_cache)
        if self.__static and self.__jsmodule:
            raise ValueError('Properties static and jsmodule '
                             'cannot both be true.')
    def to_obj(self, path):
        url = self.__url
        if self.__static:
            url = static_url(url)
        elif self.__jsmodule:
            url = urljoin(path, url)
        return {
            'name': self.__name,
            'url': url,
            'sync_deps': self.__sync_deps,
            'deps': self.__deps,
            'no_cache': self.__no_cache,
        }

class ScriptManager:
    script_class = Script
    def __init__(self):
        self.__scripts = {}
    def register(self, name, **info):
        if name in self.__scripts:
            raise ValueError("Script %s already registered." % name)
        self.__scripts[name] = self.script_class(name, **info)
    def get_info(self, path):
        return {name: script.to_obj(path) for name, script
                in self.__scripts.items()}

script_manager = ScriptManager()
