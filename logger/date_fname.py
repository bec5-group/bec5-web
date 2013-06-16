import os
from os import path as _path
import datetime
from django.dispatch import Signal

class DateFileStream(object):
    changed = Signal(providing_args=['old_name', 'new_name'])
    closed = Signal(providing_args=['name'])
    opened = Signal(providing_args=['name'])
    def __init__(self, filename_fmt, dirname, mode='a'):
        self.__fname_fmt = filename_fmt
        self.__dirname = _path.abspath(dirname)
        self.__cur_fname = None
        self.__cur_stream = None
        self.__mode = mode
    def __get_stream(self):
        d = datetime.datetime.now()
        fname = d.strftime(self.__fname_fmt)
        full_name = _path.join(self.__dirname, fname)
        if full_name == self.__cur_fname:
            return
        old_fname = self.__cur_fname
        try:
            if self.__cur_stream is not None:
                self.closed.send_robust(sender=self, name=old_fname)
                self.__cur_stream.close()
        except:
            pass
        self.__cur_stream = open(full_name, self.__mode)
        self.opened.send_robust(sender=self, name=full_name)
        if old_fname is not None:
            self.changed.send_robust(sender=self, new_name=full_name,
                                     old_name=old_fname)
        self.__cur_fname = full_name
    @property
    def stream(self):
        self.__get_stream()
        return self.__cur_stream
