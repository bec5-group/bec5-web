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

def find_scripts():
    for app in settings.INSTALLED_APPS:
        try:
            __import__(app + '.scripts')
        except ImportError:
            pass

find_scripts()