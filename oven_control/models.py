from django.db import models
from django.db.models.signals import post_save, post_delete
from . import controller

class TempController(models.Model):
    name = models.CharField(unique=True, max_length=1000)
    addr = models.CharField(max_length=1000)
    port = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    order = models.FloatField(default=0.0)
    default_temp = models.FloatField(default=0.0)
    class Meta:
        ordering = ['order', 'default_temp', 'name']
        permissions = (
            ('set_temp', "Can set controller temperatures."),
            ('set_controller', "Can change controller setting.")
        )

class TempProfile(models.Model):
    name = models.CharField(unique=True, max_length=1000)
    order = models.FloatField(default=0.0)
    class Meta:
        ordering = ['order', 'name']
        permissions = (
            ('set_profile', "Can change profile."),
            ('set_profile_temp', "Can change profile setting.")
        )

class TempSetPoint(models.Model):
    control = models.ForeignKey(TempController)
    temperature = models.FloatField(default=0.0)
    profile = models.ForeignKey(TempProfile)
    class Meta:
        ordering = ['control__order', 'control__default_temp', 'control__name']

from threading import Lock
__oven_control_model_lock = Lock()

def with_oven_control_lock(func):
    def _func(*args, **kwargs):
        with __oven_control_model_lock:
            return func(*args, **kwargs)
    _func.no_lock = func
    return _func

@with_oven_control_lock
def add_controller(name, addr, port, number, **kw):
    return TempController.objects.create(name=name, addr=addr, port=port,
                                         number=number, **kw)

@with_oven_control_lock
def get_controllers():
    return TempController.objects.all()

@with_oven_control_lock
def get_controller(cid):
    return TempController.objects.get(id=cid)

@with_oven_control_lock
def remove_controller(controller):
    try:
        if not isinstance(controller, TempController):
            controller = get_controller.no_lock(controller)
    except:
        return False
    controller.delete()
    return True


@with_oven_control_lock
def get_profiles():
    return TempProfile.objects.all()

@with_oven_control_lock
def get_profile(pid):
    return TempProfile.objects.get(id=pid)

@with_oven_control_lock
def get_profile_temps(profile, use_default=True):
    if not isinstance(profile, TempProfile):
        profile = get_profile.no_lock(profile)
    set_points = TempSetPoint.objects.filter(profile=profile)
    temps = {}
    for controller in get_controllers.no_lock():
        cid = controller.id
        try:
            temps[cid] = set_points.get(control=controller).temperature
        except:
            if use_default:
                temps[cid] = controller.default_temp
    return temps

@with_oven_control_lock
def add_profile(name, **kw):
    return TempProfile.objects.create(name=name, **kw)

@with_oven_control_lock
def set_profile_temps(profile, temps, ignore_error=True):
    if not isinstance(profile, TempProfile):
        profile = get_profile.no_lock(profile)
    temp_sets = []
    for cid, temp in temps.items():
        try:
            controller = get_controller.no_lock(cid)
            temp = float(temp)
        except:
            if not ignore_error:
                return False
            continue
        temp_sets.append((controller, temp))
    for controller, temp in temp_sets:
        TempSetPoint.objects.filter(control=controller,
                                    profile=profile).delete()
        TempSetPoint.objects.create(control=controller,
                                    profile=profile,
                                    temperature=temp)
    return True

@with_oven_control_lock
def remove_profile(profile):
    try:
        if not isinstance(profile, TempProfile):
            profile = get_profile.no_lock(profile)
    except:
        return False
    profile.delete()
    return True

class ControllerWrapper(object):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.temp = None
        self.__set_temp = None
        self.real_set_temp = None
        # create a controller for every wrapper
        # this is probably not the most elegant way but I'm too lazy to
        # write a better one (create a controller for every address/ip).
        # It will also be better to handle device number etc in wrapper
        # and use the controller object just for sending and recieving
        # messages
        self.__ctrl = controller.Controller((self.ctrl.addr, self.ctrl.port),
                                            self)
        self.__ctrl.timeout = 2
    def remove(self):
        self.__ctrl.stop()
    def check(self):
        self.__ctrl.addr = (self.ctrl.addr, self.ctrl.port)
    @property
    def dev_no(self):
        return self.ctrl.number
    @property
    def set_temp(self):
        return self.__set_temp
    @set_temp.setter
    def set_temp(self, value):
        self.__set_temp = float(value)
        self.__ctrl.activate()

class ControllerManager(object):
    def __init__(self):
        self.__ctrls = {}
        self.__profile_id = None
        self.__update_ctrl_list()
        post_save.connect(self.__post_save_cb, sender=TempController)
        post_delete.connect(self.__post_del_cb, sender=TempController)
    def __post_save_cb(self, sender, **kwargs):
        self.__update_ctrl_list()
    def __post_del_cb(self, sender, **kwargs):
        self.__update_ctrl_list()
    def __update_ctrl_list(self):
        ctrls = {}
        for ctrl in get_controllers.no_lock():
            cid = int(ctrl.id)
            try:
                ctrls[cid] = self.__ctrls[cid]
                ctrls[cid].check()
                del self.__ctrls[cid]
            except:
                ctrls[cid] = ControllerWrapper(ctrl)
        for cid, ctrl in self.__ctrls.items():
            self.__ctrls[cid].remove()
            del self.__ctrls[cid]
        self.__ctrls = ctrls
    def get_temps(self):
        return dict((cid, ctrl.temp) for (cid, ctrl)
                    in self.__ctrls.items())
    def set_temps(self, temps):
        self.__profile_id = None
        self.__set_temps(temps)
    def __set_temps(self, temps):
        for cid, temp in temps.items():
            cid = int(cid)
            try:
                self.__ctrls[cid].set_temp = float(temp)
            except:
                pass
        return True
    def set_profile(self, profile):
        self.__profile_id = profile
        self.__set_temps(get_profile_temps(profile))
        return True
    @with_oven_control_lock
    def get_setpoint(self):
        try:
            profile_name = get_profile.no_lock(self.__profile_id).name
        except:
            profile_name = None
        return {
            'id': self.__profile_id,
            'name': profile_name,
            'temps': dict((cid, ctrl.set_temp) for (cid, ctrl)
                          in self.__ctrls.items())
        }

controller_manager = ControllerManager()
