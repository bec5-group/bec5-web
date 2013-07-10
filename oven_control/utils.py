from becv_utils.network import send_once

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

def hex2temp(hexstr):
    x = int(hexstr[-6:], 16)
    s = -1 if (x & (1 << 23)) else 1
    d = (x >> 20) & 7
    v = x & 0xfffff
    if d > 5 or d < 2:
        d = 1
    return s * v / 10.0**(d - 1)

def to_ins(args, **kwargs):
    if callable(args):
        return args()
    return lambda func: func(*args, **kwargs)

@to_ins
def set_attr():
    class attr_setter(object):
        def __init__(self, attrs):
            self.__attrs = attrs
        def __getattr__(self, attr):
            return attr_setter(self.__attrs + (attr,))
        def __call__(self, obj):
            for attr in self.__attrs[:-1]:
                obj = getattr(obj, attr)
            def _deco(func):
                setattr(obj, self.__attrs[-1], func)
                return func
            return _deco
    class _set_attr(object):
        def __getattr__(self, name):
            return attr_setter((name,))
    return _set_attr()

def _handle_ret(handler, prefix, res):
    l = len(prefix)
    for r in res.decode('utf-8').split('\r'):
        if not r.startswith(prefix):
            continue
        return handler(r[l:])
    return

def wrap_cmd(cmd, use_dev_no=True):
    def _wrap_cmd(func):
        if not use_dev_no:
            def _func(addr, prefix, grp_no, *args, **kwargs):
                cmd_args = func(*args, **kwargs)
                full_cmd = "%0.2X%s" % (grp_no, cmd)
                s = "%s%s%s\r" % (prefix, full_cmd, cmd_args)
                return _handle_ret(_func.__ret_handler, full_cmd,
                                   send_once(addr, s))
        else:
            def _func(addr, prefix, grp_no, dev_no, *args, **kwargs):
                cmd_args = func(*args, **kwargs)
                full_cmd = "%0.2X%s%0.2X" % (grp_no, cmd, dev_no)
                s = "%s%s%s\r" % (prefix, full_cmd, cmd_args)
                return _handle_ret(_func.__ret_handler, full_cmd,
                                   send_once(addr, s))
        @to_ins((lambda res: True,))
        @set_attr.ret_handler(_func)
        def _(ret_func):
            _func.__ret_handler = ret_func
            return _func
        _func.use_dev_no = use_dev_no
        _func.__name__ = func.__name__
        return _func
    return _wrap_cmd

@wrap_cmd('W')
def write_set(t):
    return temp2hex(t)

@wrap_cmd('Z')
def reset_dev():
    return ''

@wrap_cmd('R')
def read_set():
    return ''

@read_set.ret_handler
def read_set(res):
    return hex2temp(res)

@wrap_cmd('X')
def read_temp():
    return ''

@read_temp.ret_handler
def read_temp(res):
    return float(res)
