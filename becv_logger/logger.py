#!/usr/bin/env python
#   Copyright (C) 2013~2013 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

class BaseLogger:
    def _log_handler(self, level, *arg, **kwargs):
        pass
    def log(self, level, *arg, **kwargs):
        try:
            self._log_handler(level, *arg, **kwargs)
        except:
            # from becv_utils import print_except
            # print_except()
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
