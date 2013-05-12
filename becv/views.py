from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
from django.contrib.auth import views as auth_views
import json

_login = auth_views.login

def login(req, *args, **kwargs):
    if req.method == 'POST' and not req.POST.get('remember', None):
        req.session.set_expiry(0)
    return _login(req, *args, **kwargs)
auth_views.login = login

def home(request):
    if not request.user.is_authenticated():
        return redirect_to_login(request.path)
    return render(request, 'home.html')

def tojson(obj, cb):
    try:
        jsonstr = json.dumps(obj)
    except:
        jsonstr = '{}'
    if cb is None:
        return jsonstr
    return "%s(%s)" % (cb, jsonstr)

def auth_jsonp(func):
    def _func(request, *args, **kwargs):
        if request.method == 'GET':
            cb = request.GET.get("jscallback", None)
        elif request.method == 'POST':
            cb = request.POST.get("jscallback", None)
        else:
            cb = None
        if not request.user.is_authenticated():
            return HttpResponse(tojson(None, cb),
                                content_type="application/json",
                                status=401)
        return func(request, *args, callback=cb, **kwargs)
    return _func

@auth_jsonp
def set_profile(request, profile=None, callback=None):
    return HttpResponse(tojson(True, callback),
                        content_type="application/json")

@auth_jsonp
def get_profiles(request, callback=None):
    profiles = [{
        'id': 'off',
        'name': 'Off',
        'temps': {
            'out': 240,
            'middle': 220,
            'bottom': 200
            }
    }, {
        'id': 'stand_by',
        'name': 'Stand By',
        'temps': {
            'out': 525,
            'middle': 480,
            'bottom': 460
            }
    }, {
        'id': 'on',
        'name': 'On',
        'temps': {
            'out': 525,
            'middle': 500,
            'bottom': 480
            }
    }]
    return HttpResponse(tojson(profiles, callback),
                        content_type="application/json")

@auth_jsonp
def get_ovens(request, callback=None):
    ovens = [{
        'id': 'bottom',
        'name': 'Bottom'
    }, {
        'id': 'middle',
        'name': 'Middle'
    }, {
        'id': 'out',
        'name': 'Out'
    }]
    return HttpResponse(tojson(ovens, callback),
                        content_type="application/json")

@auth_jsonp
def get_temps(request, callback=None):
    import random
    temps = {
        'out': 500 + random.randrange(-100, 100) / 10.0,
        'middle': 480 + random.randrange(-100, 100) / 10.0,
        'bottom': 460 + random.randrange(-100, 100) / 10.0
    }
    return HttpResponse(tojson(temps, callback),
                        content_type="application/json")
