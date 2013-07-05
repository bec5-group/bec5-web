from __future__ import print_function
import threading

__print_lock = threading.Lock()

def _print_with_style(prefix, suffix, *arg, **kwarg):
    with __print_lock:
        end = '\n'
        if 'end' in kwarg:
            end = kwarg['end']
        kwarg['end'] = ''
        print(prefix, end='')
        print(*arg, **kwarg)
        print(suffix, end=end)

def printr(*arg, **kwarg):
    _print_with_style('\033[31;1m', '\033[0m', *arg, **kwarg)

def printg(*arg, **kwarg):
    _print_with_style('\033[32;1m', '\033[0m', *arg, **kwarg)

def printy(*arg, **kwarg):
    _print_with_style('\033[33;1m', '\033[0m', *arg, **kwarg)

def printb(*arg, **kwarg):
    _print_with_style('\033[34;1m', '\033[0m', *arg, **kwarg)

def printp(*arg, **kwarg):
    _print_with_style('\033[35;1m', '\033[0m', *arg, **kwarg)

def printbg(*arg, **kwarg):
    _print_with_style('\033[36;1m', '\033[0m', *arg, **kwarg)

import traceback
def print_except():
    try:
        printr(traceback.format_exc())
    except:
        pass

def print_stack():
    try:
        printg(''.join(traceback.format_stack()[:-1]))
    except:
        pass
