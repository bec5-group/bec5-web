import os
from os import path as _path
import datetime
import time
from becv_utils import ObjSignal

class DateFileBase(object):
    changed = ObjSignal(providing_args=['old_name', 'new_name'])
    closed = ObjSignal(providing_args=['name'])
    opened = ObjSignal(providing_args=['name'])

class DateFileStream(DateFileBase):
    def __init__(self, filename_fmt, dirname, mode='a', file_open=open,
                 read_mode='r', read_open=open):
        self.__fname_fmt = filename_fmt
        self.__dirname = _path.abspath(dirname)
        self.__cur_fname = None
        self.__cur_stream = None
        self.__mode = mode
        self.__file_open = file_open
        self.__read_mode = read_mode
    def calc_name(self, d):
        d = d.replace(microsecond=0)
        fname = d.strftime(self.__fname_fmt)
        return _path.join(self.__dirname, fname)
    def __get_stream(self):
        full_name = self.calc_name(datetime.datetime.now())
        if full_name == self.__cur_fname:
            return
        old_fname = self.__cur_fname
        try:
            if self.__cur_stream is not None:
                self.closed.send_robust(name=old_fname)
                self.__cur_stream.close()
        except:
            pass
        self.__cur_stream = self.__file_open(full_name, self.__mode)
        self.opened.send_robust(name=full_name)
        if old_fname is not None:
            self.changed.send_robust(new_name=full_name, old_name=old_fname)
        self.__cur_fname = full_name
    @property
    def stream(self):
        self.__get_stream()
        return self.__cur_stream

class TimeLog(DateFileBase):
    def __init__(self, filename_fmt, dirname, binary=False):
        self.__date_strm = DateFileStream(filename_fmt, dirname,
                                          mode='ba' if binary else 'a')
        bind_signal(self.__date_strm.opened, self.opened)
        bind_signal(self.__date_strm.changed, self.changed)
        bind_signal(self.__date_strm.closed, self.closed)
    def write(self, data):
        return self.write_record(self.__date_strm.stream, time.time(),
                                 datetime.datetime.now().replace(microsecond=0))
    def write_record(self, strm, timestamp, d, data):
        pass
    def read_records(self, strm):
        pass
