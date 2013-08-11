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
from django.http import HttpResponse
from .static_loader import load_static
from .manage import script_manager, static_url
import json
from urllib.parse import urljoin
from django.conf import settings

def _script_info():
    return 'ScriptLoader.register(%s);' % json.dumps(script_manager.get_info())

def _static_info():
    return ('ScriptLoader._set_static_prefix(%s);' %
            json.dumps(settings.STATIC_URL))

def module_info(request):
    return (HttpResponse(_script_info() + _static_info(),
                         content_type="application/javascript"))

def _write_load_script(url):
    return "document.write('<script src=%s></script>');" % json.dumps(url)

def loader(request):
    return (HttpResponse(
        _write_load_script(static_url('jsmodule/js/script-loader.js'))
        + _write_load_script(urljoin(request.path, 'module-info.js')),
        content_type="application/javascript"))
