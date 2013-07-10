#!/usr/bin/env python

import json

class Obj(object):
    pass

ctrl_names = {
    '1': "Bottom",
    '2': "Middle",
    '3': "Out"
}
profile_names = {
    '1': "Off",
    '2': "Stand By",
    '3': "On"
}
def get_controller(cid):
    res = Obj()
    res.name = ctrl_names[str(cid)]
    return res
def get_profile(pid):
    res = Obj()
    res.name = profile_names[str(pid)]
    return res

__loggers = {}

def reg_logger(name):
    def _deco(func):
        __loggers[name] = func
        return func
    return _deco

@reg_logger('add_controller')
def _add_controller_logger(GET):
    GET = GET.get
    return ('Name: %s, Address: %s:%s, NO: %s, Order: %s, '
            'Default Temperature: %s' %
            (GET('name'), GET('addr'), GET('port'), GET('number'),
             GET('order'), GET('default_temp')))

@reg_logger('set_controller')
def _set_controller_logger(GET, cid=None):
    GET = GET.get
    ctrl = get_controller(cid)
    old_name = ctrl.name
    name = GET('name')
    if name == old_name:
        return ('Name: %s, Address: %s:%s, NO: %s, Order: %s, '
                'Default Temperature: %s' %
                (name, GET('addr'), GET('port'), GET('number'),
                 GET('order'), GET('default_temp')))
    return ('Name: %s, New Name: %s, Address: %s:%s, NO: %s, Order: %s, '
            'Default Temperature: %s' %
            (old_name, name, GET('addr'), GET('port'), GET('number'),
             GET('order'), GET('default_temp')))

@reg_logger('del_controller')
def _del_controller_logger(GET, cid=None):
    ctrl = get_controller(cid)
    return 'Name: %s' % ctrl.name

@reg_logger('edit_profile')
def _edit_profile_logger(GET, profile=None, name=None, order=None):
    profile = get_profile(profile)
    res = 'Name: ' + profile.name
    if name and name != profile.name:
        res = res + ', New Name: ' + name
    if order is not None:
        res = res + ', Order: ' + order
    if len(GET):
        res = res + ', Temperatures: { '
        for cid, temp in GET.items():
            try:
                ctrl = get_controller(cid)
                res += ctrl.name + ': ' + temp + ', '
            except:
                pass
        res = res + '}'
    return res

@reg_logger('add_profile')
def _add_profile_logger(GET, name=None, order=None):
    res = 'Name: ' + name
    if order is not None:
        res = res + ', Order: ' + order
    if len(GET):
        res = res + ', Temperatures: { '
        for cid, temp in GET.items():
            try:
                ctrl = get_controller(cid)
                res += ctrl.name + ': ' + temp + ', '
            except:
                pass
        res = res + '}'
    return res

@reg_logger('del_profile')
def _del_profile_logger(GET, pid=None):
    profile = get_profile(pid)
    return 'Name: ' + profile.name

@reg_logger('set_temps')
def _set_temps_logger(GET):
    res = ''
    for cid, temp in GET.items():
        try:
            ctrl = get_controller(cid)
            res += ctrl.name + ': ' + temp + ', '
        except:
            pass
    return res

@reg_logger('set_profile')
def _set_profile_logger(GET, profile=None):
    profile = get_profile(profile)
    return 'Name: ' + profile.name

def add_msg(line):
    obj = json.loads(line)
    c = obj['c']
    if not 'msg' in c:
        if c['a'] in __loggers:
            c['msg'] = __loggers[c['a']](c.get('GET'), *c.get('arg', []),
                                         **c.get('kw', {}))
        else:
            c['msg'] = ''
    return json.dumps(obj, separators=(',', ':')) + '\n'

def main():
    import sys
    ifile, ofile = sys.argv[1:]
    with open(ifile) as fh:
        lines = fh.readlines()
    new_lines = [add_msg(l) for l in lines]
    with open(ofile, 'w') as fh:
        fh.write(''.join(new_lines))

if __name__ == '__main__':
    main()
