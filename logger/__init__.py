import logging
import os
from os import path as _path
import time
from .date_fname import DateFileStream
from .logger import BaseLogger
import json
import threading
import gzip

def open_append_gzip(fname, mode):
    try:
        with gzip.open(fname, 'r') as fh:
            data = fh.read()
    except:
        data = ''
    fh = gzip.open(fname, 'w')
    fh.write(data)
    return fh

class TimeLogger(BaseLogger):
    def __init__(self, filename_fmt='%Y-%m-%d.log', dirname='', **kwargs):
        BaseLogger.__init__(self)
        self.__stm_factory = DateFileStream(filename_fmt, dirname,
                                            'a', **kwargs)
        self.__lock = threading.Lock()

    @property
    def stream(self):
        return self.__stm_factory.stream

    def _log_handler(self, level, **kwargs):
        with self.__lock:
            content = dict((k, v) for (k, v) in kwargs.items()
                           if (v or v == False))
            stm = self.stream
            json.dump({'l': level, 't': int(time.time()),
                       'c': content}, stm, separators=(',', ':'))
            stm.write('\n')
            stm.flush()
