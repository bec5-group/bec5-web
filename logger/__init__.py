import logging
import os
from os import path as _path
import time
from .date_fname import DateFileStream, TimeLogger
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
