import time

class ErrorLogger(object):
    def __init__(self):
        self.__errors = {}
    def _error_logger_handle(self, is_error, name, msg):
        pass
    def get_errors(self):
        return [{'name': name, 'msg': err['msg']}
                for name, err in self.__errors.items() if err['error']]
    def clear_error(self, name):
        cur_time = int(time.time())
        err_obj = self.__errors.get(name, {'time': None, 'error': False,
                                           'msg': ''})
        if err_obj['error']:
            err_obj['error'] = False
            try:
                self._error_logger_handle(name, False, 'error cleared.')
            except:
                pass
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
        try:
            self._error_logger_handle(name, True, msg)
        except:
            pass
