import os
from os import path as _path
import datetime
import time
from becv_utils import ObjSignal, bind_signal
from .logger import BaseLogger
from .record_cache import RecordCache
import json
import threading

class DateFileBase(object):
    changed = ObjSignal(providing_args=['old_name', 'new_name'])
    closed = ObjSignal(providing_args=['name'])
    opened = ObjSignal(providing_args=['name'])

class DateFileStream(DateFileBase):
    def __init__(self, filename_fmt, dirname, mode='a', file_open=open,
                 read_mode='r', read_open=open):
        self.__fname_fmt = filename_fmt
        self.__dirname = _path.abspath(dirname)
        self.__cur_fname = None
        self.__cur_stream = None
        self.__mode = mode
        self.__file_open = file_open
        self.__read_mode = read_mode
        self.__read_open = read_open
    def open_read(self, fname):
        return self.__read_open(fname, self.__read_mode)
    def calc_name(self, d):
        try:
            d = datetime.datetime.fromtimestamp(int(d))
        except:
            pass
        d = d.replace(microsecond=0)
        fname = d.strftime(self.__fname_fmt)
        return _path.join(self.__dirname, fname)
    def __get_stream(self):
        full_name = self.calc_name(datetime.datetime.now())
        if full_name == self.__cur_fname:
            return
        old_fname = self.__cur_fname
        try:
            if self.__cur_stream is not None:
                self.closed.send_robust(name=old_fname)
                self.__cur_stream.close()
        except:
            pass
        self.__cur_stream = self.__file_open(full_name, self.__mode)
        self.opened.send_robust(name=full_name)
        if old_fname is not None:
            self.changed.send_robust(new_name=full_name, old_name=old_fname)
        self.__cur_fname = full_name
    @property
    def stream(self):
        self.__get_stream()
        return self.__cur_stream

def _json_reader(stm):
    while True:
        line = stm.readline()
        if not line:
            return
        try:
            yield json.loads(line)
        except:
            pass

def find_next_fname(calc_name, t, name, max_t):
    if t >= max_t:
        return None, None
    l_t = int(t)
    l_n = name
    r_t = int(max_t)
    r_n = calc_name(r_t)
    if l_n == r_n:
        return None, None
    while r_t - l_t >= 2:
        m_t = (l_t + r_t) // 2
        m_n = calc_name(m_t)
        if m_n == l_n:
            l_t = m_t
        else:
            r_t = m_t
            r_n = m_n
    return r_t, r_n

class TimeLogger(BaseLogger, DateFileBase, RecordCache):
    def __init__(self, filename_fmt='%Y-%m-%d.log', dirname='',
                 record_num=20000, **kwargs):
        BaseLogger.__init__(self)
        DateFileBase.__init__(self)
        RecordCache.__init__(self, record_num)

        self.__stm_factory = DateFileStream(filename_fmt, dirname, **kwargs)
        bind_signal(self.__stm_factory.opened, self.opened)
        bind_signal(self.__stm_factory.changed, self.changed)
        bind_signal(self.__stm_factory.closed, self.closed)

        self.__lock = threading.Lock()
        self.__cur_record = None
        self.__cur_fname = None
        self.opened.connect(self.__on_file_open)

    def __on_file_open(self, name='', **kwargs):
        if self.__cur_fname == name:
            return
        if self.__cur_fname is not None:
            self._put_cache(self.__cur_fname, self.__cur_record)
        self.__cur_fname = name
        self.__cur_record = []

    @property
    def stream(self):
        return self.__stm_factory.stream

    def _record_getter(self, key):
        try:
            with self.__stm_factory.open_read(key) as stm:
                return self._read_record_objs(stm)
        except:
            # from becv_utils import print_except
            # print_except()
            return []
    def _log_handler(self, level, *args, **kwargs):
        obj = self._to_record_obj(level, int(time.time()), *args, **kwargs)
        stm = self.stream
        with self.__lock:
            self.__cur_record.append(obj)
            self._write_record_obj(stm, obj)
            stm.flush()
    def get_records(self, _from, to=None, max_count=None):
        return list(self.get_records_it(_from, to=to, max_count=max_count))
    def get_records_it(self, _from, to=None, max_count=None):
        _from = int(_from)
        if to is None:
            to = time.time()
        else:
            to = int(to)
        calc_name = self.__stm_factory.calc_name
        cur_time = _from
        cur_name = calc_name(_from)
        count = 0
        while True:
            cur_recs = self.get(cur_name)
            for rec in cur_recs:
                t = self._get_record_obj_time(rec)
                if t > to:
                    return
                if t > cur_time:
                    cur_time = t
                if t < _from:
                    continue
                count += 1
                yield t, rec
                if max_count is not None and count >= max_count:
                    return
            cur_time, cur_name = find_next_fname(calc_name, cur_time,
                                                 cur_name, to)
            if cur_name is None:
                return

    # To be override
    def _to_record_obj(self, l, t, **kwargs):
        content = dict((k, v) for (k, v) in kwargs.items()
                       if (v or v == False))
        return {'l': level, 't': int(time.time()), 'c': content}
    def _write_record_obj(self, stm, obj):
        json.dump(obj, stm, separators=(',', ':'))
        stm.write('\n')
    def _get_record_obj_time(self, obj):
        return obj['t']
    def _read_record_objs(self, stm):
        return list(_json_reader(stm))
