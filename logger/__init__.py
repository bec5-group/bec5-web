import logging
import os
from os import path as _path
import datetime

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
        self.__fname_fmt = filename_fmt
        self.__dirname = _path.abspath(dirname)
        self.__cur_fname = None
        self.__cur_stream = None

    def __get_stream(self):
        d = datetime.datetime.now()
        fname = d.strftime(self.__fname_fmt)
        full_name = _path.join(self.__dirname, fname)
        if full_name == self.__cur_fname:
            return
        try:
            self.__cur_stream.close()
        except:
            pass
        self.__cur_stream = open(full_name, 'a')
        self.__cur_fname = full_name

    @property
    def stream(self):
        self.__get_stream()
        return self.__cur_stream
