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

from time import sleep
import time
import json
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.utils import timezone as dj_tz

from becv_utils import printr, printg, printy, printb
from becv_utils.thread_helper import WithHelper, repeat_call
from becv_utils.math import to_finite, fix_non_finite
from logger.error_logger import ErrorLogger
from logger import TimeLogger, bin_logger

from . import utils
from . import models

ctrl_logger = TimeLogger(filename_fmt='controller_action-%Y-%m-%d.json',
                         dirname=settings.LOGGING_DIR)

class Controller(WithHelper, ErrorLogger):
    def ctrl_cmd(cmd_func):
        def cmd_method(self, *args, **kwargs):
            res = cmd_func(self.__addr, *args, **kwargs)
            if res is None:
                printr(cmd_func.__name__, self.__addr, args, res)
            else:
                printg(cmd_func.__name__, self.__addr, args, res)
            return res
        cmd_method.use_dev_no = getattr(cmd_func, 'use_dev_no', True)
        return cmd_method
    write_set = ctrl_cmd(utils.write_set)
    read_set = ctrl_cmd(utils.read_set)
    read_temp = ctrl_cmd(utils.read_temp)
    reset_dev = ctrl_cmd(utils.reset_dev)
    del ctrl_cmd
    def __init__(self, addr, mgr):
        WithHelper.__init__(self)
        ErrorLogger.__init__(self)
        self.__addr = addr
        self.__mgr = mgr
        self.__disp_set_temp = None
        self.start()
        self.__need_reset = False
    def _error_logger_handle(self, name, is_error, msg):
        if is_error:
            ctrl_logger.error(name=name, msg=msg, addr=self.__addr,
                              ctrl=self.__mgr.ctrl.name)
        else:
            ctrl_logger.info(name=name, msg=msg, addr=self.__addr,
                             ctrl=self.__mgr.ctrl.name)
    def stop(self):
        WithHelper.stop(self)
        del self.__mgr
    @property
    def addr(self):
        return self.__addr
    @addr.setter
    def addr(self, addr):
        self.__addr = addr
    @property
    def temp(self):
        return self.__mgr.temp
    @temp.setter
    def temp(self, value):
        self.__mgr.temp = value
    @property
    def set_temp(self):
        return self.__mgr.set_temp
    @set_temp.setter
    def set_temp(self, value):
        self.__mgr.set_temp = value
    @property
    def real_set_temp(self):
        return self.__mgr.real_set_temp
    @real_set_temp.setter
    def real_set_temp(self, value):
        self.__mgr.real_set_temp = value
    @property
    def dev_no(self):
        return self.__mgr.dev_no
    def __reset_set_temp(self):
        res = repeat_call(self.reset_dev, ('*', self.dev_no, 2), n=3,
                          wait_time=0.2)
        if not res is None:
            self.__need_reset = False
            self.clear_error('reset_set_temp')
        else:
            self.set_error('reset_set_temp', 'Reset Controller failed.')
    def __update_set_temp(self):
        res = repeat_call(self.write_set,
                          ('*', self.dev_no, 2, self.set_temp),
                          n=3, wait_time=0.2)
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
                          n=3, wait_time=0.1)
        if not res is None:
            self.clear_error('update_disp_temp')
        else:
            self.set_error('update_disp_temp',
                           'Update Controller setpoint display failed.')
    def __get_real_temp(self):
        temp = repeat_call(self.read_temp, ('*', self.dev_no, 1), n=3,
                           wait_time=0.1)
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
                                    wait_time=0.1)
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
                                    wait_time=0.1)
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
        if self.__need_reset:
            reseted = True
            self.__reset_set_temp()
        if (self.set_temp is not None and
            (self.__disp_set_temp is None or not self.__disp_temp_ok())):
            self.__update_disp_temp()
        if reseted:
            sleep(2.5)
        else:
            sleep(.5)
        self.__get_real_temp()
        sleep(.1)
        self.__get_set_temp()
        sleep(.1)
        self.__get_disp_temp()

class ControllerWrapper(object):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.__temp = None
        self.__set_temp = None
        self.real_set_temp = None
        self.__json_fname = None
        # create a controller for every wrapper
        # this is probably not the most elegant way but I'm too lazy to
        # write a better one (create a controller for every address/ip).
        # It will also be better to handle device number etc in wrapper
        # and use the controller object just for sending and recieving
        # messages
        self.__ctrl = Controller((self.ctrl.addr, self.ctrl.port), self)
        self.__ctrl.timeout = 10
        log_name_fmt = ('temp_log_%s' % self.ctrl.id) + '-%Y-%m-%d.log'
        self.__logger = bin_logger.FloatDateLogger(log_name_fmt,
                                                   settings.DATA_LOG_DIR)
        self.__logger.opened.connect(self.__on_log_open)
    def get_errors(self):
        return self.__ctrl.get_errors()
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
        ctrl = self.ctrl
        setting = {
            'name': ctrl.name,
            'addr': ctrl.addr,
            'port': ctrl.port,
            'number': ctrl.number
        }
        old_setting = self.__get_old_setting(fname, setting)
        if old_setting is None:
            return
        if settings.USE_TZ:
            cur_tz = dj_tz.get_current_timezone()
            timestr = dj_tz.now().astimezone(cur_tz).strftime(
                '%Y-%m-%d_%H:%M:%S@%z')
        else:
            timestr = dj_tz.now().strftime('%Y-%m-%d_%H:%M:%S')
        setting['time'] = timestr
        setting['time_stamp'] = time.time()
        old_setting.append(setting)
        with open(fname, 'w') as fh:
            ctrl = self.ctrl
            content = json.dumps(old_setting, indent=2)
            fh.write(content)
    @property
    def temp(self):
        return self.__temp
    @temp.setter
    def temp(self, value):
        value = to_finite(value)
        self.__temp = value
        self.__logger.info(value)
    def remove(self):
        self.__ctrl.stop()
        self.__logger.close()
    def check(self):
        self.__ctrl.addr = self.ctrl.addr, self.ctrl.port
        if self.__json_fname is not None:
            self.__write_setting()
    @property
    def dev_no(self):
        return self.ctrl.number
    @property
    def set_temp(self):
        return self.__set_temp
    @set_temp.setter
    def set_temp(self, value):
        self.__set_temp = to_finite(value)
        self.__ctrl.activate()
    @property
    def logger(self):
        return self.__logger

class ControllerManager(object):
    def __init__(self):
        self.__ctrls = {}
        self.__profile_id = None
        self.__update_ctrl_list()
        post_save.connect(self.__post_save_cb, sender=models.TempController)
        post_delete.connect(self.__post_del_cb, sender=models.TempController)
    def __post_save_cb(self, sender, **kwargs):
        self.__update_ctrl_list()
    def __post_del_cb(self, sender, **kwargs):
        self.__update_ctrl_list()
    def __update_ctrl_list(self):
        ctrls = {}
        for ctrl in models.get_controllers.no_lock():
            cid = int(ctrl.id)
            try:
                ctrls[cid] = self.__ctrls[cid]
                ctrls[cid].ctrl = ctrl
                ctrls[cid].check()
                del self.__ctrls[cid]
            except:
                ctrls[cid] = ControllerWrapper(ctrl)
        for cid, ctrl in self.__ctrls.items():
            self.__ctrls[cid].remove()
            del self.__ctrls[cid]
        self.__ctrls = ctrls
    def get_errors(self):
        errors = {}
        for cid, ctrl in self.__ctrls.items():
            ctrl_errors = ctrl.get_errors()
            if ctrl_errors:
                errors[cid] = {'name': ctrl.ctrl.name,
                               'errors': ctrl_errors}
        return errors
    def get_temps(self):
        return dict((cid, fix_non_finite(ctrl.temp)) for (cid, ctrl)
                    in self.__ctrls.items())
    def set_temps(self, temps):
        self.__profile_id = None
        return self.__set_temps(temps)
    def __set_temps(self, temps):
        for cid, temp in temps.items():
            cid = int(cid)
            try:
                self.__ctrls[cid].set_temp = to_finite(temp)
            except:
                pass
        return True
    def set_profile(self, profile):
        if not profile:
            return
        self.__profile_id = profile
        self.__set_temps(models.get_profile_temps(profile))
        return True
    @models.with_oven_control_lock
    def get_setpoint(self):
        try:
            profile_name = models.get_profile.no_lock(self.__profile_id).name
        except:
            profile_name = None
        return {
            'id': self.__profile_id,
            'name': profile_name,
            'temps': dict((cid, fix_non_finite(ctrl.set_temp)) for (cid, ctrl)
                          in self.__ctrls.items())
        }
    def get_loggers(self):
        return dict((cid, ctrl.logger) for (cid, ctrl) in self.__ctrls.items())

if not getattr(__import__('__main__'), '_django_syncdb', False):
    controller_manager = ControllerManager()
