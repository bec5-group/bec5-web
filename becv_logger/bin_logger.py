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

import struct
from .date_fname import TimeLogger
from becv_utils import print_except
import time

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
    """
    Class to log binary data.
    """
    def __init__(self, filename_fmt, dirname, fmt, **kwargs):
        self.__fmt = fmt
        TimeLogger.__init__(self, filename_fmt, dirname, mode='ab',
                            read_mode='rb', **kwargs)
    def _to_record_obj(self, l, t, *args):
        return (t,) + args
    def _write_record_obj(self, stm, obj):
        write_struct_fh(stm, self.__fmt, (obj,))
    def _get_record_obj_time(self, obj):
        return obj[0]
    def _read_record_objs(self, stm):
        return load_struct_fh(stm, self.__fmt)

class FloatDateLogger(BinDateLogger):
    """
    Class to do averaging when retrieving logging data.
    """
    def __init__(self, filename_fmt, dirname, **kwargs):
        BinDateLogger.__init__(self, filename_fmt, dirname, '<Qd', **kwargs)
    def __get_range_it_limited(self, _from, to, max_count):
        if _from >= to:
            return
        base_it = self.get_records_it(_from, to)
        try:
            last_t, v = next(base_it)
        except:
            return
        _from = max(last_t, _from)
        yield last_t, v
        dt = (to - _from) * 0.8 / max_count
        cur_ts = []
        cur_vs = []
        for t, v in base_it:
            if t - last_t < dt:
                cur_ts.append(t)
                cur_vs.append(v)
                continue
            l = len(cur_ts)
            if l:
                last_t = cur_ts[-1]
                yield sum(cur_ts) / l, sum(cur_vs) / l
                if t - last_t < dt:
                    cur_ts = [t]
                    cur_vs = [v]
                    continue
                cur_ts = []
                cur_vs = []
            last_t = t
            yield t, v
    def get_range_it(self, _from, to=None, max_count=None):
        if max_count is None or max_count < 0:
            return self.get_records_it(_from, to)
        _from = int(float(_from))
        try:
            to = float(to)
            if to < 0:
                raise ValueError
        except:
            to = time.time()
        to = int(to)
        return self.__get_range_it_limited(_from, to, max_count)
    def get_range(self, _from, to=None, max_count=None):
        return list(self.get_range_it(_from, to=to, max_count=max_count))
