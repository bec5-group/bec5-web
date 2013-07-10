import socket

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
