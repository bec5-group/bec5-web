from json_view import JSONPError, return_jsonp, auth_jsonp
from . import models
from .models import with_room_temp_lock

@return_jsonp
def get_servers(request):
    return [{'id': server.id,
             'name': server.name}
             for server in models.get_servers()]

@return_jsonp
@auth_jsonp
def get_server_setting(request, sid=None):
    server = models.get_server(sid)
    return dict((key, getattr(server, key))
                for key in ('id', 'name', 'addr', 'port', 'order'))

def _add_server_logger(request):
    GET = request.GET.get
    return ('Name: %s, Address: %s:%s, Order: %s' %
            (GET('name'), GET('addr'), GET('port'), GET('order')))

@return_jsonp
@auth_jsonp('room_temp.edit_server', log=_add_server_logger)
def add_server(request):
    server = models.add_server(
        request.GET['name'], request.GET['addr'], request.GET['port'],
        order=request.GET.get('order'))
    return {
        'id': server.id,
        'name': server.name,
    }

def _edit_server_logger(request, sid=None):
    GET = request.GET.get
    server = models.get_server(sid)
    old_name = server.name
    name = GET('name')
    if name == old_name:
        return ('Name: %s, Address: %s:%s, Order: %s' %
                (name, GET('addr'), GET('port'), GET('order')))
    return ('Name: %s, New Name: %s, Address: %s:%s, Order: %s' %
            (old_name, name, GET('addr'), GET('port'), GET('order')))

@return_jsonp
@auth_jsonp('room_temp.edit_server', log=_edit_server_logger)
def edit_server(request, sid=None):
    server = models.get_server(sid)
    for key in ('name', 'addr', 'port', 'order'):
        if key in request.GET:
            setattr(server, key, request.GET[key])
    server.save()
    return {
        'id': server.id,
        'name': server.name,
    }

def _del_server_logger(request, sid=None):
    server = models.get_server(sid)
    return 'Name: %s' % server.name

@return_jsonp
@auth_jsonp('room_temp.edit_server', log=_del_server_logger)
def del_server(request, sid=None):
    return models.remove_server(sid)

@return_jsonp
@with_room_temp_lock
def get_devices(request):
    res = {}
    for device in models.get_devices.no_lock():
        sid = device.server.id
        sobj = res.get(sid, {})
        sobj[device.id] = device.name
        res[sid] = sobj
    return res

@return_jsonp
@auth_jsonp
def get_device_setting(request, did=None):
    device = models.get_device(did)
    return {
        'id': device.id,
        'name': device.name,
        'unit': device.unit,
        'order': device.order,
        'server': device.server.id,
        'server_name': device.server.name,
    }

def _add_device_logger(request):
    GET = request.GET.get
    server = models.get_server(request.GET['server'])
    return ('Name: %s, Server: %s, Unit: %s, Order: %s' %
            (GET('name'), server.name, GET('unit'), GET('order')))

@return_jsonp
@auth_jsonp('room_temp.edit_server', log=_add_device_logger)
def add_device(request):
    GET = request.GET.get
    device = models.add_device(request.GET['server'], request.GET['name'],
                               unit=GET('unit'), order=GET('order'))
    return {
        'id': device.id,
        'name': device.name,
    }

def _edit_device_logger(request, did=None):
    GET = request.GET.get
    device = models.get_device(did)
    old_name = device.name
    name = GET('name')
    try:
        server = models.get_server(request.GET['server'])
    except:
        server = None
    if name is None or name == old_name:
        res = 'Name: %s' % name
    else:
        res = 'Name: %s, New Name: %s' % (old_name, name)
    if server is not None:
        res = res + 'Server: %s' % server.name
    if GET('unit') is not None:
        res = res + 'Unit: %s' % GET('unit')
    if GET('order') is not None:
        res = res + 'Order: %s' % GET('order')
    return res

@return_jsonp
@auth_jsonp('room_temp.edit_server', log=_edit_device_logger)
def edit_device(request, did=None):
    device = models.get_device(did)
    try:
        device.server = models.get_server(request.GET['server'])
    except:
        pass
    for key in ('name', 'unit', 'order'):
        if key in request.GET:
            setattr(device, key, request.GET[key])
    server.save()
    return {
        'id': device.id,
        'name': device.name,
    }

def _del_device_logger(request, did=None):
    device = models.get_device(did)
    return 'Name: %s' % device.name

@return_jsonp
@auth_jsonp('room_temp.edit_server', log=_del_device_logger)
def del_device(request, did=None):
    return models.remove_device(did)
