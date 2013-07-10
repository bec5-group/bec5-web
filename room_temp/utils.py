from becv_utils.network import send_once

def query_value(addr, name):
    cmd = '"%s.Value?"\n' % name
    try:
        return float(send_once(addr, cmd))
    except:
        return
