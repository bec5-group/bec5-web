#!/usr/bin/env python2
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

import threading

class LinkedList(object):
    __slots__ = ['prev', 'next']
    def __init__(self):
        self.__init_link()
    def __init_link(self):
        self.prev = self
        self.next = self
    def __remove(self):
        self.prev.next = self.next
        self.next.prev = self.prev
    def remove(self):
        self.__remove()
        self.__init_link()
    def destroy(self):
        self.__remove()
        self.prev = None
        self.next = None
    def insert(self, ele):
        ele.__remove()
        ele.prev = self
        ele.next = self.next
        self.next.prev = ele
        self.next = ele
    def insert_before(self, ele):
        ele.__remove()
        ele.next = self
        ele.prev = self.prev
        self.prev.next = ele
        self.prev = ele

class _CacheItem(LinkedList):
    __slots__ = ['prev', 'next', 'data', 'count', 'key']
    def __init__(self, key, data):
        LinkedList.__init__(self)
        self.data = data
        self.key = key
        self.update_count()
    def update_count(self):
        try:
            self.count = max(len(self.data), 1)
        except:
            self.count = 1
    def __str__(self):
        return str(self.data)
    def __repr__(self):
        return repr(self.data)

class RecordCache(LinkedList):
    def __init__(self, record_num):
        LinkedList.__init__(self)
        self.__record_num = record_num
        self.__lock = threading.Lock()
        self.__cache = {}
        self.__count = 0
    def _record_getter(self, key):
        pass
    def _rec_iter(self):
        rec = self.prev
        while rec is not self:
            yield rec
            rec = rec.prev
    def __repr__(self):
        with self.__lock:
            return repr(dict((rec.key, rec.data)
                             for rec in self._rec_iter()))
    __str__ = __repr__
    def get(self, key):
        try:
            with self.__lock:
                rec = self.__cache[key]
                rec.remove()
                self.insert(rec)
                return rec.data
        except:
            pass
        record = self._record_getter(key)
        self._put_cache(key, record)
        return record
    def _put_cache(self, key, records):
        with self.__lock:
            try:
                rec = self.__cache[key]
                rec.data = records
                old_count = rec.count
                rec.update_count()
                new_count = rec.count
                self.__count += new_count - old_count
                rec.remove()
                self.insert(rec)
                return
            except:
                pass
            while self.__count > self.__record_num:
                if self.prev is self:
                    self.__count = 0
                    break
                self.__count -= self.prev.count
                old_rec = self.prev
                del self.__cache[old_rec.key]
                old_rec.destroy()
            rec = _CacheItem(key, records)
            self.insert(rec)
            self.__count += rec.count
            self.__cache[key] = rec
