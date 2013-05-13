from urllib import urlencode
from urllib2 import Request
from pyquery import PyQuery as pq

def url_request(url, params, method="GET"):
    if method == "POST":
        return Request(url, data=urlencode(params))
    else:
        return Request(url + "?" + urlencode(params))

__max_v = 1 << 20
def temp2hex(v):
    x = 0
    if v < 0:
        x = 1 << 23
        v = -v
    if v > __max_v:
        v = __max_v
    v = int(v * 10) | (1 << 21) | x
    return "%0.6X" % v

def set_device(url, passwd, n, vs):
    req = {
        'PW': passwd,
        'N': n
    }
    for i, v in enumerate(vs):
        req["X%d" % (i + 1)] = v
        req["S%d" % (i + 1)] = temp2hex(v)
    return url_request(url + '/setpoint', req, 'POST')

def set_point(url, passwd, n, v):
    return set_device(url, passwd, n, [v, v, 0, 0])

def hexstr2temp(hexstr):
    x = int(hexstr.split('R')[-1][2:], 16)
    s = -1 if (x & (1 << 23)) else 1
    d = (x >> 20) & 7
    v = x & 0xfffff
    if d > 5 or d < 2:
        d = 1
    return s * v / 10.0**(d - 1)

def get_setpoint(s):
    return hexstr2temp(pq(s)('input[type="hidden"][name="S1"]').attr("value"))
