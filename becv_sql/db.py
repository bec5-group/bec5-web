#   Copyright (C) 2013~2014 by Yichao Yu
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

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker, Session
from threading import Lock

class BEC5Sql:
    class RollBack(Exception):
        pass

    __lock = Lock()
    __sql = None
    __sqls = {}
    @classmethod
    def instance(cls, url=None):
        with cls.__lock:
            if cls.__sql is None:
                cls.__sql = cls(url)
                return cls.__sql
            if url is None or url == cls.__sql.__url:
                return cls.__sql
            try:
                return cls.__sqls[url]
            except KeyError:
                cls.__sqls[url] = cls(url)
                return cls.__sqls[url]
    def __init__(self, url):
        self.__url = url
        self.__engine = create_engine(url, echo=False)
        class BEC5Session(Session):
            def __enter__(self):
                return self
            def __exit__(self, _type, _value, traceback):
                if _type is None:
                    self.commit()
                    self.close()
                elif _type is BEC5Sql.RollBack:
                    return True
                return False
        self.__Session = sessionmaker(bind=self.__engine, class_=BEC5Session)

        _engine = self.__engine
        class BEC5BaseMeta(DeclarativeMeta):
            def __init__(cls, name, bases, dct):
                DeclarativeMeta.__init__(cls, name, bases, dct)
                cls.metadata.create_all(_engine)
        self.__Base = declarative_base(metaclass=BEC5BaseMeta)

    @property
    def engine(self):
        return self.__engine
    @property
    def Session(self):
        return self.__Session
    @property
    def session(self):
        return self.__Session()
    @property
    def Base(self):
        return self.__Base
