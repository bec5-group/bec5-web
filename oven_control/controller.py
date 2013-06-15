import threading
from . import models as ctrl_models
from . import utils
import weakref

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
        self.__helper.timeout = value
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
    def __init__(self, addr):
        WithHelper.__init__(self)
        self.__addr = addr
        self.__devs = {}
        self.start()
    def add_dev(self, dev_type, dev_addr, *args):
        pass
    def run(self):
        pass

class NotReadyException(Exception):
    pass

def not_ready_on_none(func):
    def _func(*arg, **args):
        res = func(*arg, **args)
        if res is None:
            raise NotReadyException
        return res
    return _func

def ret_last(func):
    def _func(*args):
        func(*args)
        return args[-1]
    return _func

def to_callable(func):
    class C:
        def __call__(self, *args, **kwargs):
            return func(*args, **kwargs)
    return C()

class ControllerWorker(object):
    def __init__(self, ctrl, prefix, grp_no, dev_no):
        self.__ctrl = ctrl
        self.__prefix = prefix
        self.__grp_no = grp_no
        self.__dev_no = dev_no
    @to_callable
    def ctrl_cmd(cmd_func, res_none=False):
        use_dev_no = getattr(cmd_func, 'use_dev_no', True)
        if use_dev_no:
            def send_func(self, args=(), kwargs={}):
                return cmd_func(self.__ctrl, self.__prefix, self.__grp_no, 1,
                                self.__dev_no, *args, **kwargs)
        else:
            def send_func(self, args=(), kwargs={}):
                return cmd_func(self.__ctrl, self.__prefix, self.__grp_no, 1,
                                *args, **kwargs)
        def _deco(_func):
            def func(self):
                try:
                    args = _func(self)
                except NotReadyException:
                    return
                if not args:
                    args = ()
                res = send_func(self, *args)
                if res is None:
                    func.err_cnt += 1
                    if res_none:
                        return func.__ret_handler(self, res)
                    return
                func.err_cnt = 0
                return func.__ret_handler(self, res)
            func.err_cnt = 0
            @utils.to_ins((lambda self, res: res,))
            @utils.set_attr.ret_handler(func)
            def _(__func):
                func.__ret_handler = __func
                return func
            return func
        return _deco
    @utils.set_attr.ret_handler(ctrl_cmd)
    def _(cmd_func, **kwargs):
        def __func(self):
            return
        return ControllerWorker.ctrl_cmd(cmd_func, **kwargs)(__func).ret_handler

class DevState:
    WAITING, SUCCESS, FAILED = range(3)

class SetDevice(ControllerWorker):
    def __init__(self, ctrl, prefix, grp_no, dev_no):
        ControllerWorker.__init__(self, ctrl, prefix, grp_no, dev_no)
        self.__cur_val = None
        self.__set_point = None
        self.__state = DevState.SUCCESS
    @ControllerWorker.ctrl_cmd(Controller.write_set)
    @not_ready_on_none
    def write_set(self):
        return self.__set_point
    @ControllerWorker.ctrl_cmd.ret_handler(Controller.read_set)
    @ret_last
    def read_set(self, res):
        self.__cur_val = res
    @ControllerWorker.ctrl_cmd(Controller.reset_dev)
    def reset_dev(self):
        pass
    @property
    def cur_val(self):
        return self.__cur_val
    @property
    def set_point(self):
        return self.__set_point
    @set_point.setter
    def set_point(self, val):
        self.__set_point = val
        self.__state = DevState.WAITING
