from time import sleep
import socket

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

def send_once(addr, s):
    so = socket.socket()
    try:
        so.settimeout(1)
        so.connect(addr)
        so.sendall(s.encode('utf-8'))
        res = so.recv(1000)
    except:
        res = b''
    finally:
        so.close()
    return res

def try_send(addr, s, n=1):
    for i in range(n):
        res = send_once(addr, s)
        if res:
            break
        sleep(.1)
    return res

def _handle_ret(handler, prefix, res):
    l = len(prefix)
    for r in res.decode('utf-8').split('\r'):
        if not r.startswith(prefix):
            continue
        return handler(r[l:])
    return

def wrap_cmd(cmd, use_dev_no=True):
    _globals = {
        'ret_handler': lambda res: True
    }
    def _set_ret(ret_func):
        _globals['ret_handler'] = ret_func
        return _globals['cmd_func']
    def _wrap_cmd(func):
        if not use_dev_no:
            def _func(addr, prefix, grp_no, n, *args, **kwargs):
                cmd_args = func(*args, **kwargs)
                full_cmd = "%0.2X%s" % (grp_no, cmd)
                s = "%s%s%s\r" % (prefix, full_cmd, cmd_args)
                return _handle_ret(_globals['ret_handler'], full_cmd,
                                   try_send(addr, s, n))
        else:
            def _func(addr, prefix, grp_no, n, dev_no, *args, **kwargs):
                cmd_args = func(*args, **kwargs)
                full_cmd = "%0.2X%s%0.2X" % (grp_no, cmd, dev_no)
                s = "%s%s%s\r" % (prefix, full_cmd, cmd_args)
                return _handle_ret(_globals['ret_handler'], full_cmd,
                                   try_send(addr, s, n))
        _func.ret_handler = _set_ret
        _globals['cmd_func'] = _func
        _func.use_dev_no = use_dev_no
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
