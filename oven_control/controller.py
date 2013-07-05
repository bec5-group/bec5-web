import threading
from . import utils
import weakref
from time import sleep
import time

from becv_utils import printr, printg, printy, printb
from becv import settings
from logger import TimeLogger, open_append_gzip
import gzip

ctrl_logger = TimeLogger(filename_fmt='controller_action-%Y-%m-%d.json.gz',
                         dirname=settings.LOGGING_DIR,
                         file_open=open_append_gzip,
                         read_open=gzip.open)

# Run parent's .run() periodically or when activated in a separate thread.
class ThreadHelper(object):
    def __init__(self, parent):
        self.__parent = weakref.ref(parent)
        self.__event = threading.Event()
        self.__thread = threading.Thread(target=self.__run)
        self.__timeout = 1
        self.__running = False
    def activate(self):
        self.__event.set()
    @property
    def parent(self):
        return self.__parent()
    @property
    def timeout(self):
        return self.__timeout
    @timeout.setter
    def timeout(self, value):
        if not value or value <= 0:
            value = None
        self.__timeout = value
    def start(self):
        self.__running = True
        self.__thread.start()
    def stop(self):
        self.__running = False
        self.activate()
    def __run_iter(self):
        parent = self.parent
        if parent is None:
            return False
        try:
            parent.run()
        except:
            from becv_utils import print_except
            print_except()
        return True
    def __run(self):
        while self.__running:
            self.__event.wait(self.timeout)
            self.__event.clear()
            if not self.__run_iter():
                break

# class that uses ThreadHelper
class WithHelper(object):
    def __init__(self):
        self.__helper = ThreadHelper(self)
    def run(self):
        pass
    def activate(self):
        return self.__helper.activate()
    def start(self):
        return self.__helper.start()
    def stop(self):
        return self.__helper.stop()
    @property
    def timeout(self):
        return self.__helper.timeout
    @timeout.setter
    def timeout(self, value):
        old_value = self.__helper.timeout
        self.__helper.timeout = value
        if value != old_value:
            self.activate()
    def __del__(self):
        self.__helper.stop()

print_lock = threading.Lock()

def repeat_call(func, args=(), kwargs={}, n=1, wait_time=0, wait_first=True):
    res = None
    for i in range(n):
        if (i or wait_first) and wait_time > 0:
            sleep(wait_time)
        res = func(*args, **kwargs)
        if res is not None:
            break
    return res

class Controller(WithHelper):
    def ctrl_cmd(cmd_func):
        def cmd_method(self, *args, **kwargs):
            res = cmd_func(self.__addr, *args, **kwargs)
            with print_lock:
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
        self.__addr = addr
        self.__mgr = mgr
        self.__disp_set_temp = None
        self.start()
        self.__need_reset = False
        self.__errors = {}
    def stop(self):
        WithHelper.stop(self)
        del self.__mgr
    def get_errors(self):
        return dict((name, err['msg']) for name, err in self.__errors.items()
                    if err['error'])
    def clear_error(self, name):
        cur_time = int(time.time())
        err_obj = self.__errors.get(name, {'time': None, 'error': False,
                                           'msg': ''})
        if err_obj['error']:
            ctrl_logger.info(name=name, msg='error cleared.',
                             addr=self.__addr, ctrl=self.__mgr.ctrl.name)
            err_obj['error'] = False
        err_obj['time'] = cur_time
        self.__errors[name] = err_obj
    def set_error(self, name, msg):
        err_obj = self.__errors.get(name, {'time': None, 'error': True,
                                           'msg': ''})
        last_t = err_obj['time']
        cur_time = int(time.time())
        if last_t is not None and (last_t > cur_time - 100 or
                                   (last_t > cur_time - 600 and
                                    err_obj['error'])):
            return
        err_obj['time'] = cur_time
        err_obj['error'] = True
        err_obj['msg'] = msg
        self.__errors[name] = err_obj
        ctrl_logger.error(name=name, msg=msg, addr=self.__addr,
                          ctrl=self.__mgr.ctrl.name)
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
            (self.real_set_temp is None or self.__set_temp_ok())):
            self.__update_set_temp()
        if self.__need_reset:
            reseted = True
            self.__reset_set_temp()
        if (self.set_temp is not None and
            (self.__disp_set_temp is None or self.__disp_temp_ok())):
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
