import logging
import os
from os import path as _path
import time
from .date_fname import DateFileStream
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

class TimeLogger(object):
    def __init__(self, filename_fmt='%Y-%m-%d.log', dirname='', **kwargs):
        self.__stm_factory = DateFileStream(filename_fmt, dirname,
                                            'a', **kwargs)
        self.__lock = threading.Lock()

    @property
    def stream(self):
        return self.__stm_factory.stream

    def log(self, level, **kwargs):
        with self.__lock:
            try:
                content = dict((k, v) for (k, v) in kwargs.items()
                               if (v or v == False))
                stm = self.stream
                json.dump({'l': level, 't': int(time.time()),
                           'c': content}, stm, separators=(',', ':'))
                stm.write('\n')
                stm.flush()
            except:
                pass

    def info(self, **kwargs):
        self.log('INFO', **kwargs)
    def error(self, **kwargs):
        self.log('ERROR', **kwargs)
    def debug(self, **kwargs):
        self.log('DEBUG', **kwargs)
    def fatal(self, **kwargs):
        self.log('FATAL', **kwargs)
    def critical(self, **kwargs):
        self.log('CRITICAL', **kwargs)
    def warning(self, **kwargs):
        self.log('WARNING', **kwargs)
    def warn(self, **kwargs):
        self.log('WARNING', **kwargs)
