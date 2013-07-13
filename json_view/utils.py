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
from becv_utils import print_except
import json
from django.http import HttpResponse
from logger import TimeLogger

auth_logger = TimeLogger(filename_fmt='auth_action_log-%Y-%m-%d.json',
                         dirname=settings.LOGGING_DIR)

def tojson(obj, cb):
    try:
        jsonstr = json.dumps(obj, separators=(',', ':'))
    except:
        jsonstr = '{}'
    if cb is None:
        return jsonstr
    return "%s(%s)" % (cb, jsonstr)

class JSONPError(Exception):
    def __init__(self, errno=500):
        self.errno = errno

def return_jsonp(func):
    def _func(request, *args, **kwargs):
        if request.method == 'GET':
            cb = request.GET.get("jscallback", None)
        elif request.method == 'POST':
            cb = request.POST.get("jscallback", None)
        else:
            cb = None
        try:
            return HttpResponse(tojson(func(request, *args, **kwargs), cb),
                                content_type="application/json")
        except JSONPError as jsonp_err:
            return HttpResponse(tojson(None, cb), status=jsonp_err.errno,
                                content_type="application/json")
        except:
            print_except()
            return HttpResponse(tojson(None, cb), status=500,
                                content_type="application/json")
    _func.__name__ = func.__name__
    return _func

def arg_deco(func):
    def _func(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return func(args[0])
        def _deco(__func):
            return func(__func, *args, **kwargs)
        return _deco
    _func.__name__ = func.__name__
    return _func

@arg_deco
def auth_jsonp(func, *perms, **_kw):
    log = _kw.get('log')
    def _func(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            raise JSONPError(401)
        if log:
            log_obj = {
                'arg': args,
                'kw': kwargs,
                'GET': request.GET,
                'a': func.__name__,
                'u': user.username,
                'msg': log(request, *args, **kwargs)
            }
        for perm in perms:
            if not user.has_perm(perm):
                if log:
                    auth_logger.error(**log_obj)
                raise JSONPError(403)
        if log:
            auth_logger.info(**log_obj)
        return func(request, *args, **kwargs)
    _func.__name__ = func.__name__
    return _func
