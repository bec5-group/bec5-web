#!/usr/bin/env python2
from __future__ import print_function, division
from django.utils import six
import struct
from .date_fname import TimeLogger

def write_struct_fh(fh, fmt, it):
    for l in it:
        fh.write(struct.pack(fmt, *l))

def write_struct(fname, fmt, it):
    with open(fname, 'wb') as fh:
        return write_struct_fh(fh, fmt, it)

def struct_loader(fh, fmt):
    size = struct.calcsize(fmt)
    while True:
        line = fh.read(size)

        if not line or len(line) != size:
            return
        yield struct.unpack(fmt, line)

def load_struct_fh(fh, fmt):
    return list(struct_loader(fh, fmt))

def load_struct(fname, fmt):
    with open(fname, 'rb') as fh:
        return load_struct_fh(fh, fmt)

class BinDateLogger(TimeLogger):
    def __init__(self, filename_fmt, dirname, fmt, **kwargs):
        TimeLogger.__init__(self, filename_fmt, dirname, mode='ab',
                            read_mode='rb', **kwargs)
        self.__fmt = fmt
    def _to_record_obj(self, l, t, *args):
        return (t,) + args
    def _write_record_obj(self, stm, obj):
        write_struct_fh(stm, self.__fmt, (obj,))
    def _get_record_obj_time(self, obj):
        return obj[0]
    def _read_record_objs(self, stm):
        return load_struct_fh(stm, self.__fmt)
