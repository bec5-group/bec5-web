import weakref
import threading
from . import print_except

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
