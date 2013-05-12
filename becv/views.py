from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
import json

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
