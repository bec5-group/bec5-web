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

from .utils import return_jsonp, auth_jsonp, auth_logger
from jsmodule import set_context as set_js_context

def set_context(request):
    return set_js_context({
        'json_view_prefix': urljoin(request.path, '$')[:-1]
    })

def get_log_view(logger):
    @return_jsonp
    @auth_jsonp
    def get_logs(request):
        max_count = 1000
        GET = request.GET
        logs = logger.get_records(GET.get('from'), GET.get('to'), max_count + 1)
        if len(logs) > max_count:
            return {
                'logs': logs[:max_count],
                'is_all': False
            }
        return {
            'logs': logs,
            'is_all': True
        }
    return get_logs

get_logs = get_log_view(auth_logger)
