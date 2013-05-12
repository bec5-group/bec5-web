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
        return "%s(%s)" % (cb, json.dumps(obj))
    except:
        return "{}"

def auth_jsonp(func):
    def _func(request, *args, **kwargs):
        cb = request.GET.get("jscallback", "cb")
        if not request.user.is_authenticated():
            return HttpResponse(tojson(False, cb),
                                content_type="application/json",
                                status=401)
        return func(request, *args, callback=cb, **kwargs)

@auth_jsonp
def set_oven(request, action=None, callback=None):
    return HttpResponse(tojson(True, callback),
                        content_type="application/json")
