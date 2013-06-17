import os
from os import path as _path
import datetime
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

class ObjSignal(property, Signal):
    def __init__(self, *args, **kwargs):
        property.__init__(self, self.__get_signal_wrapper)
        Signal.__init__(self, *args, **kwargs)
    def __get_signal_wrapper(self, obj):
        return SignalWrapper(self, obj)

class DateFileBase(object):
    changed = ObjSignal(providing_args=['old_name', 'new_name'])
    closed = ObjSignal(providing_args=['name'])
    opened = ObjSignal(providing_args=['name'])

class DateFileStream(DateFileBase):
    def __init__(self, filename_fmt, dirname, mode='a'):
        self.__fname_fmt = filename_fmt
        self.__dirname = _path.abspath(dirname)
        self.__cur_fname = None
        self.__cur_stream = None
        self.__mode = mode
    def __get_stream(self):
        d = datetime.datetime.now().replace(microsecond=0)
        fname = d.strftime(self.__fname_fmt)
        full_name = _path.join(self.__dirname, fname)
        if full_name == self.__cur_fname:
            return
        old_fname = self.__cur_fname
        try:
            if self.__cur_stream is not None:
                self.closed.send_robust(name=old_fname)
                self.__cur_stream.close()
        except:
            pass
        self.__cur_stream = open(full_name, self.__mode)
        self.opened.send_robust(name=full_name)
        if old_fname is not None:
            self.changed.send_robust(new_name=full_name, old_name=old_fname)
        self.__cur_fname = full_name
    @property
    def stream(self):
        self.__get_stream()
        return self.__cur_stream

class TimeLog(DateFileBase):
    def __init__(self, filename_fmt, dirname):
        pass
    def write_record(self, stm, t, *args, **kwargs):
        pass
