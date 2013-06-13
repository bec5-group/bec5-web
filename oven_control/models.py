from django.db import models

class TempController(models.Model):
    name = models.CharField(unique=True, max_length=1000)
    addr = models.CharField(max_length=1000)
    port = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    order = models.FloatField(default=0.0)
    default_temp = models.FloatField(default=0.0)
    class Meta:
        ordering = ['order', 'default_temp', 'name']

class TempProfile(models.Model):
    name = models.CharField(unique=True, max_length=1000)
    order = models.FloatField(default=0.0)
    class Meta:
        ordering = ['order', 'name']

class TempSetPoint(models.Model):
    control = models.ForeignKey(TempController)
    temperature = models.FloatField(default=0.0)
    profile = models.ForeignKey(TempProfile)
    class Meta:
        ordering = ['control__order', 'control__default_temp', 'control__name']

# TODO lock

def add_controller(name, addr, port, number, **kw):
    return TempController.objects.create(name=name, addr=addr, port=port,
                                         number=number, **kw)

def get_controllers():
    return TempController.objects.all()

def get_controller(cid):
    return TempController.objects.get(id=cid)

def remove_controller(controller):
    try:
        if not isinstance(controller, TempController):
            controller = get_controller(controller)
    except:
        return False
    controller.delete()
    return True


def get_profiles():
    return TempProfile.objects.all()

def get_profile(pid):
    return TempProfile.objects.get(id=pid)

def get_profile_temps(profile, use_default=True):
    if not isinstance(profile, TempProfile):
        profile = get_profile(profile)
    set_points = TempSetPoint.objects.filter(profile=profile)
    temps = {}
    for controller in get_controllers():
        cid = controller.id
        try:
            temps[cid] = set_points.get(control=controller).temperature
        except:
            if use_default:
                temps[cid] = controller.default_temp
    return temps

def add_profile(name, **kw):
    return TempProfile.objects.create(name=name, **kw)

def set_profile_temps(profile, temps, ignore_error=True):
    if not isinstance(profile, TempProfile):
        profile = get_profile(profile)
    temp_sets = []
    for cid, temp in temps.items():
        try:
            controller = get_controller(cid)
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

def remove_profile(profile):
    try:
        if not isinstance(profile, TempProfile):
            profile = get_profile(profile)
    except:
        return False
    profile.delete()
    return True
