from django.dispatch import Signal

class SignalWrapper(object):
    def __init__(self, signal, obj):
        self.__signal = signal
        self.__obj = obj
    def __getattr__(self, key):
        val = getattr(self.__signal, key)
        if key in ('connect', 'disconnect', 'has_listener'):
            def func(*args, **kwargs):
                if not 'sender' in kwargs:
                    kwargs['sender'] = self.__obj
                return val(*args, **kwargs)
            return func
        if key in ('send', 'send_robust'):
            def func(*args, **kwargs):
                if len(args) == 0:
                    args = (self.__obj,)
                return val(*args, **kwargs)
            return func
        return val

class ObjSignal(Signal):
    def __init__(self, *args, **kwargs):
        Signal.__init__(self, *args, **kwargs)
    def __get__(self, obj, owner):
        if obj is None:
            return self
        return SignalWrapper(self, obj)

def bind_signal(src, dst):
    src.connect(lambda sender=None, **kwargs: dst.send_robust(sender, **kwargs))
