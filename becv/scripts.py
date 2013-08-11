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
Register site level scripts. Do not put libraries (should go to jsmodule/static)
or scripts that are related to certain apps (should go to <app>/static) here.
"""

from jsmodule import register_script

_main_scripts = {
    'home_app': {
        'url': "js/home.js",
        'static': True,
        'deps': ('angular', 'angular.ui.bootstrap', 'angular.gravatar',
                 'angular.md5', 'becv.logging', 'becv.request',
                 'becv.room_temp', 'becv.log_mgr', 'becv.popup_form',
                 'bootstrap', 'bootstrap.datetimepicker'),
        'sync_deps': ('angular.loader',),
    },
    'login_app': {
        'url': "js/login.js",
        'static': True,
        'deps': ('angular', 'angular.ui.bootstrap',),
        'sync_deps': ('angular.loader',),
    },
}

for name, info in _main_scripts.items():
    register_script(name, **info)
