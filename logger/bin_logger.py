#!/usr/bin/env python2
from __future__ import print_function, division
from django.utils import six
import struct
from .date_fname import DateFileStream

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
    return tuple(struct_loader(fh, fmt))

def load_struct(fname, fmt):
    with open(fname, 'rb') as fh:
        return load_struct_fh(fh, fmt)

class BinDateLogger(DateFileStream):
    def __init__(self, filename_fmt, dirname, fmt, **kwargs):
        DateFileStream.__init__(self, filename_fmt, dirname, mode='ab',
                                **kwargs)
        self.__fmt = fmt
    def write_struct(self, *args):
        stm = self.stream
        try:
            write_struct_fh(stm, self.__fmt, (args,))
            stm.flush()
        except:
            pass
