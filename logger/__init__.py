import logging
import os
from os import path as _path
import datetime
from .date_fname import DateFileStream

class TimeLogHandler(logging.StreamHandler):
    """
    This class is like a StreamHandler using sys.stderr, but always uses
    whatever sys.stderr is currently set to rather than the value of
    sys.stderr at handler construction time.
    """
    def __init__(self, filename_fmt='%Y-%m-%d.log', dirname=''):
        """
        Initialize the handler.
        """
        logging.Handler.__init__(self)
        self.__stm_factory = DateFileStream(filename_fmt, dirname, 'a')

    @property
    def stream(self):
        return self.__stm_factory.stream
