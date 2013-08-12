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
Scan through all installed apps and import the `scripts` submodule.
TODO?: also import `scripts` submodule of the main app.
"""

from django.conf import settings
from . import register_script

def find_scripts():
    main_script = '.'.join(settings.ROOT_URLCONF.split('.')[:-1])
    for app in tuple(settings.INSTALLED_APPS) + (main_script,):
        try:
            for name, info in __import__(app + '.scripts').jsmodules.items():
                register_script(name, **info)
        except ImportError:
            pass
        except AttributeError:
            pass

find_scripts()
