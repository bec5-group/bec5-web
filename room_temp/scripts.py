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

from django.core.urlresolvers import reverse
from .views import set_context

jsmodules = {
    'becv.room_temp': {
        'url': "room_temp/js/room-temp.js",
        'static': True,
        'sync_deps': ('angular.loader', 'becv.room_temp_context',),
        'deps': ('angular', 'becv.request', 'becv.logging',
                 'becv.popup_form', 'angular.ui.bootstrap'),
    },
    'becv.room_temp_context': {
        'url': reverse(set_context),
        'no_cache': True,
    },
}
