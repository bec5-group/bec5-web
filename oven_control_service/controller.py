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

import os
import time
import json
from datetime import datetime as _datetime
from time import sleep

from dateutil.tz import tzlocal
from gi.repository import GLib, GObject

from becv_utils import printr, printg, printy, printb
from becv_utils.misc import run_no_sync, debug as _debug, RefParent, WithLock
from becv_utils.math import to_finite, fix_non_finite
from becv_utils.thread_helper import WithHelper, repeat_call
from becv_logger import TimeLogger, bin_logger
from becv_logger.error_logger import ErrorLogger

from . import utils

class Controller(GObject.Object, WithHelper, ErrorLogger,
                 RefParent, WithLock):
    def ctrl_cmd(cmd_func):
        def cmd_method(self, *args, **kwargs):
            res = cmd_func(self.addr, *args, **kwargs)
            if _debug:
                if res is None:
                    printr(cmd_func.__name__, self.addr, args, res)
                else:
                    printg(cmd_func.__name__, self.addr, args, res)
            return res
        cmd_method.__name__ = cmd_func.__name__
        cmd_method.use_dev_no = getattr(cmd_func, 'use_dev_no', True)
        return cmd_method
    write_set = ctrl_cmd(utils.write_set)
    read_set = ctrl_cmd(utils.read_set)
    read_temp = ctrl_cmd(utils.read_temp)
    reset_dev = ctrl_cmd(utils.reset_dev)
    del ctrl_cmd
    id = GObject.property(type=str)
    name = GObject.property(type=str)
    url = GObject.property(type=str)
    port = GObject.property(type=int)
    dev_no = GObject.property(type=int, default=0)
    @property
    def addr(self):
        return self.url, self.port

    @property
    def temp(self):
        return self.__temp
    @temp.setter
    def temp(self, value):
        value = to_finite(value)
        self.__temp = value
        self.__data_logger.info(value)
    @property
    def set_temp(self):
        return self.__set_temp
    @set_temp.setter
    def set_temp(self, value):
        self.__set_temp = to_finite(value)
        self.activate()
    @property
    def real_set_temp(self):
        return self.__real_set_temp
    @real_set_temp.setter
    def real_set_temp(self, value):
        self.__real_set_temp = value
    def __init__(self, ctrl, mgr):
        GObject.Object.__init__(self)
        WithHelper.__init__(self)
        WithLock.__init__(self)
        ErrorLogger.__init__(self)
        RefParent.__init__(self, mgr)

        self.__temp = None
        self.__set_temp = None
        self.__real_set_temp = None
        self.__disp_set_temp = None
        self.__json_fname = None
        self.__need_reset = False
        self.__data_logger = None
        self.__log_name_fmt = ('temp_log_%s' % self.id) + '-%Y-%m-%d.log'

        self.update(ctrl)
        self.timeout = 10
        self.set_log_path(self.parent.log_dir)
        self.start()
    @property
    @WithLock.with_lock
    def data_logger(self):
        return self.__data_logger
    @WithLock.with_lock
    def set_log_path(self, dirname):
        if dirname is None:
            return
        self.__json_fname = None
        if self.__data_logger is not None:
            self.__data_logger.close()
            del self.__data_logger
        self.__data_logger = bin_logger.FloatDateLogger(self.__log_name_fmt,
                                                        dirname)
        self.__data_logger.opened.connect(self.__on_log_open)
    def __on_log_open(self, sender=None, name=None, **kwargs):
        if name.endswith('.log'):
            name = name[:-4]
        name = name + '.json'
        self.__json_fname = name
        try:
            self.__write_setting()
        except:
            pass
    def __get_old_setting(self, fname, setting):
        try:
            with open(fname) as fh:
                saved_settings = json.load(fh)
            last_setting = saved_settings[-1]
            for k, v in setting.items():
                if last_setting[k] != v:
                    return saved_settings
            return
        except:
            return []
    def __write_setting(self):
        fname = self.__json_fname
        setting = {
            'name': self.name,
            'addr': self.addr,
            'port': self.port,
            'number': self.dev_no
        }
        old_setting = self.__get_old_setting(fname, setting)
        if old_setting is None:
            return
        tz = tzlocal()
        setting['time_stamp'] = time.time()
        setting['time'] = _datetime.now(tz).strftime('%Y-%m-%d_%H:%M:%S@%z')
        old_setting.append(setting)
        with open(fname, 'w') as fh:
            content = json.dumps(old_setting, indent=2)
            fh.write(content)
    def update(self, ctrl):
        self.freeze_notify()
        try:
            with self.lock:
                self.id = str(ctrl['id'])
                self.dev_no = int(ctrl['number'])
                self.url = ctrl['addr']
                self.name = ctrl['name']
                self.port = int(ctrl['port'])
        finally:
            self.thaw_notify()
        if self.__json_fname is not None:
            self.__write_setting()
    def _error_logger_handle(self, name, is_error, msg):
        if is_error:
            self.parent.logger.error(name=name, msg=msg, addr=self.addr,
                                     ctrl=self.name)
        else:
            self.parent.logger.info(name=name, msg=msg, addr=self.addr,
                                    ctrl=self.name)
    def remove(self):
        self.stop()
        if self.__data_logger is not None:
            self.__data_logger.close()
            self.__data_logger = None
    def __reset_set_temp(self):
        res = repeat_call(self.reset_dev, ('*', self.dev_no, 2), n=3,
                          wait_time=0.4)
        if not res is None:
            self.__need_reset = False
            self.clear_error('reset_set_temp')
        else:
            self.set_error('reset_set_temp', 'Reset Controller failed.')
    def __update_set_temp(self):
        res = repeat_call(self.write_set,
                          ('*', self.dev_no, 2, self.set_temp),
                          n=3, wait_time=0.4)
        # Always reset no matter if a valid response is received since
        # the server may have got the correct value (and therefore return
        # the right value when we ask for the set point), in such case
        # the set temp function will not be run again (which is the only way
        # to set need_reset).
        self.__need_reset = True
        if not res is None:
            self.clear_error('update_set_temp')
        else:
            self.set_error('update_set_temp',
                           'Update Controller setpoint failed.')
    def __update_disp_temp(self):
        res = repeat_call(self.write_set, ('*', self.dev_no, 1, self.set_temp),
                          n=3, wait_time=0.4)
        if not res is None:
            self.clear_error('update_disp_temp')
        else:
            self.set_error('update_disp_temp',
                           'Update Controller setpoint display failed.')
    def __get_real_temp(self):
        temp = repeat_call(self.read_temp, ('*', self.dev_no, 1), n=3,
                           wait_time=0.4)
        # result can be 0.0 if the controller is reset
        if temp:
            self.temp = temp
        if not temp is None:
            self.clear_error('get_real_temp')
        else:
            self.set_error('get_real_temp',
                           'Get Oven Temperature failed.')
    def __get_set_temp(self):
        real_set_temp = repeat_call(self.read_set, ('*', self.dev_no, 2), n=3,
                                    wait_time=0.4)
        if real_set_temp:
            self.real_set_temp = real_set_temp
            # init set point using the value from the device
            if self.set_temp is None:
                self.set_temp = real_set_temp
        if not real_set_temp is None:
            self.clear_error('get_set_temp')
            if self.__set_temp_ok():
                self.clear_error('update_set_temp')
        else:
            self.set_error('get_set_temp',
                           'Get setpoint failed.')
    def __get_disp_temp(self):
        disp_set_temp = repeat_call(self.read_set, ('*', self.dev_no, 1), n=3,
                                    wait_time=0.4)
        if disp_set_temp:
            self.__disp_set_temp = disp_set_temp
        if not disp_set_temp is None:
            self.clear_error('get_disp_temp')
            if self.__disp_temp_ok():
                self.clear_error('update_disp_temp')
        else:
            self.set_error('get_disp_temp',
                           'Get display setpoint failed.')
    def __set_temp_ok(self):
        return (self.set_temp is not None and
                self.real_set_temp is not None and
                -0.15 <= (self.real_set_temp - self.set_temp) <= 0.15)
    def __disp_temp_ok(self):
        return (self.set_temp is not None and
                self.__disp_set_temp is not None and
                -0.15 <= (self.__disp_set_temp - self.set_temp) <= 0.15)
    def run(self):
        reseted = False
        if (self.set_temp is not None and
            (self.real_set_temp is None or not self.__set_temp_ok())):
            self.__update_set_temp()
            sleep(.4)
        if self.__need_reset:
            reseted = True
            self.__reset_set_temp()
            sleep(.4)
        if (self.set_temp is not None and
            (self.__disp_set_temp is None or not self.__disp_temp_ok())):
            self.__update_disp_temp()
            sleep(0.4)
        if reseted:
            sleep(2)
        else:
            sleep(1)
        self.__get_real_temp()
        sleep(.5)
        self.__get_set_temp()
        sleep(.5)
        self.__get_disp_temp()

@run_no_sync
class manager(GObject.Object, WithLock):
    __gsignals__ = {
        'dev-added': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'dev-removed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }
    def __init__(self):
        GObject.Object.__init__(self)
        WithLock.__init__(self)
        self.__ctrls = {}
        self.__logger = None
        self.__log_dir = None
    def __getitem__(self, cid):
        return self.__ctrls[cid]
    @property
    def log_dir(self):
        return self.__log_dir
    @property
    def logger(self):
        return self.__logger
    @WithLock.with_lock
    def set_log_path(self, dirname):
        if self.__log_dir == dirname:
            return
        logger = TimeLogger(filename_fmt='controller_action-%Y-%m-%d.json',
                            dirname=dirname)
        if self.__logger is not None:
            self.__logger.close()
            del self.__logger
        self.__logger = logger
        self.__log_dir = dirname
        for cid, ctrl_obj in self.__ctrls.items():
            ctrl_obj.set_log_path(log_dir)
    profile_id = GObject.property(type=str)
    @WithLock.with_lock
    def __set_controllers(self, ctrls):
        dev_added = set()
        dev_removed = set()
        ctrl_objs = {}
        for ctrl in ctrls:
            cid = str(ctrl['id'])
            try:
                ctrl_objs[cid] = self.__ctrls[cid]
                # ctrl_objs signal can emit here
                ctrl_objs[cid].update(ctrl)
                del self.__ctrls[cid]
            except:
                # TODO
                ctrl_objs[cid] = Controller(ctrl, self)
                dev_added.add(cid)
        for cid, ctrl_obj in self.__ctrls.items():
            ctrl_obj.remove()
            del self.__ctrls[cid]
            dev_removed.add(cid)
        self.__ctrls = ctrl_objs
        return dev_added, dev_removed
    def set_controllers(self, ctrls):
        dev_added, dev_removed = self.__set_controllers(ctrls)
        for cid in dev_added:
            self.emit('dev-added', cid)
        for cid in dev_removed:
            self.emit('dev-removed', cid)
    def set_temps(self, profile, temps):
        self.profile_id = str(profile)
        for cid, temp in temps.items():
            cid = str(cid)
            try:
                self.__ctrls[cid].set_temp = to_finite(temp)
            except:
                pass
        return True
    @WithLock.with_lock
    def get_errors(self):
        errors = {}
        for cid, ctrl in self.__ctrls.items():
            ctrl_errors = ctrl.get_errors()
            if ctrl_errors:
                errors[cid] = {'name': ctrl.name,
                               'errors': ctrl_errors}
        return errors
    @WithLock.with_lock
    def get_temps(self):
        return dict((cid, fix_non_finite(ctrl.temp)) for (cid, ctrl)
                    in self.__ctrls.items())
    @WithLock.with_lock
    def get_setpoints(self):
        return {
            'id': self.profile_id,
            'temps': dict((cid, fix_non_finite(ctrl.set_temp)) for (cid, ctrl)
                          in self.__ctrls.items())
        }
    @WithLock.with_lock
    def get_data_loggers(self):
        return dict((cid, ctrl.data_logger) for (cid, ctrl)
                    in self.__ctrls.items())
