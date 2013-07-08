#!/usr/bin/env python

class BaseLogger(object):
    def _log_handler(self, level, *arg, **kwargs):
        pass
    def log(self, level, *arg, **kwargs):
        try:
            self._log_handler(level, *arg, **kwargs)
        except:
            pass
    def info(self, *args, **kwargs):
        self.log('INFO', *args, **kwargs)
    def error(self, *args, **kwargs):
        self.log('ERROR', *args, **kwargs)
    def debug(self, *args, **kwargs):
        self.log('DEBUG', *args, **kwargs)
    def fatal(self, *args, **kwargs):
        self.log('FATAL', *args, **kwargs)
    def critical(self, *args, **kwargs):
        self.log('CRITICAL', *args, **kwargs)
    def warning(self, *args, **kwargs):
        self.log('WARNING', *args, **kwargs)
    def warn(self, *args, **kwargs):
        self.log('WARNING', *args, **kwargs)
