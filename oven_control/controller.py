import threading
from . import utils
import weakref
from time import sleep

# Run parent's .run() periodically or when activated in a separate thread.
class ThreadHelper(object):
    def __init__(self, parent):
        self.__parent = weakref.ref(parent)
        self.__event = threading.Event()
        self.__thread = threading.Thread(target=self.__run)
        self.__timeout = None
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
            pass
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

class Controller(WithHelper):
    def ctrl_cmd(cmd_func):
        def cmd_method(self, *args, **kwargs):
            return cmd_func(self.__addr, *args, **kwargs)
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
    def __get_set_temp(self):
        real_set_temp = self.read_set('*', self.dev_no, 1)
        if not real_set_temp is None:
            self.real_set_temp = real_set_temp
            # init set point using the value from the device
            if self.set_temp is None:
                self.set_temp = real_set_temp
    def __reset_set_temp(self):
        # try 3 times because this is also important...
        for i in range(3):
            if i:
                sleep(.1)
            res = self.reset_dev('*', self.dev_no, 1)
            if not res is None:
                break
    def __update_set_temp(self):
        if self.set_temp is None:
            return
        if (self.real_set_temp is None or
            not -0.15 <= (self.real_set_temp - self.set_temp) <= 0.15):
            # try 3 times because this is important...
            for i in range(3):
                if i:
                    sleep(.1)
                res = self.write_set('*', self.dev_no, 1, self.set_temp)
                if not res is None:
                    # only reset if set temperature succeeded
                    self.__reset_set_temp()
                    break
    def __get_disp_temp(self):
        disp_set_temp = self.read_set('*', self.dev_no, 2)
        if not disp_set_temp is None:
            self.__disp_set_temp = disp_set_temp
    def __update_disp_temp(self):
        if self.set_temp is None:
            return
        if (self.__disp_set_temp is None or
            not -0.15 <= (self.__disp_set_temp - self.set_temp) <= 0.15):
            self.write_set('*', self.dev_no, 2, self.set_temp)
    def __get_real_temp(self):
        temp = self.read_temp('*', self.dev_no, 1)
        if temp is not None:
            self.temp = temp
    def run(self):
        self.__get_set_temp()
        self.__update_set_temp()
        self.__get_disp_temp()
        self.__update_disp_temp()
        self.__get_real_temp()
