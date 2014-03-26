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

import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from threading import Lock

from becv_sql import BEC5Sql
from becv_utils.math import to_finite

_sql = BEC5Sql.instance()

class TempController(_sql.Base):
    __tablename__ = 'oven_ctrl__temp_controller'
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    name = sa.Column(sa.String(1000), unique=True, default='')
    addr = sa.Column(sa.String(1000), default='')
    port = sa.Column(sa.Integer, default=0)
    number = sa.Column(sa.Integer, default=0)
    order = sa.Column(sa.Float, default=0.0)
    default_temp = sa.Column(sa.Float, default=0.0)
    def __str__(self):
        return repr({k: getattr(self, k) for k
                     in ('name', 'addr', 'port', 'number', 'order',
                         'default_temp')})

class TempProfile(_sql.Base):
    __tablename__ = 'oven_ctrl__temp_profile'
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    name = sa.Column(sa.String(1000), unique=True, default='')
    order = sa.Column(sa.Float, default=0.0)
    def __str__(self):
        return repr({k: getattr(self, k) for k in ('name', 'order')})

class TempSetPoint(_sql.Base):
    __tablename__ = 'oven_ctrl__temp_set_point'
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    cid = sa.Column(sa.Integer, sa.ForeignKey('oven_ctrl__temp_controller.id'))
    pid = sa.Column(sa.Integer, sa.ForeignKey('oven_ctrl__temp_profile.id'))
    temperature = sa.Column(sa.Float, default=0.0)

    control = relationship(TempController,
                           backref=backref('setpoint', order_by=id))
    profile = relationship(TempProfile,
                           backref=backref('setpoint', order_by=id))

__oven_control_model_lock = Lock()

def with_oven_control_lock(func):
    def _func(*args, **kwargs):
        with __oven_control_model_lock:
            return func(*args, **kwargs)
    _func.no_lock = func
    return _func

def _clean_setpoint(s):
    s.query(TempSetPoint).filter((TempSetPoint.cid == None) |
                                 (TempSetPoint.pid == None)).delete()

@with_oven_control_lock
@_sql.with_session
def add_controller(s, name, addr, port, number, **kw):
    ctrl = TempController(name=name, addr=addr, port=port, number=number, **kw)
    s.add(ctrl)
    return ctrl

@with_oven_control_lock
@_sql.with_session
def get_controllers(s):
    return s.query(TempController).all()

@with_oven_control_lock
@_sql.with_session
def get_controller(s, cid):
    return s.query(TempController).filter(TempController.id == cid).all()

@with_oven_control_lock
@_sql.with_session
def remove_controller(s, controller):
    try:
        if not isinstance(controller, TempController):
            controller = get_controller.no_lock.no_session(s, controller)
    except:
        return False
    s.delete(controller)
    _clean_setpoint(s)
    return True


@with_oven_control_lock
@_sql.with_session
def get_profiles(s):
    return s.query(TempProfile).all()

@with_oven_control_lock
@_sql.with_session
def get_profile(s, pid):
    return s.query(TempProfile).filter(TempProfile.id == pid).one()

@with_oven_control_lock
@_sql.with_session
def get_profile_temps(s, profile, use_default=True):
    if isinstance(profile, TempProfile):
        profile = profile.id
    set_points = s.query(TempSetPoint).filter(TempSetPoint.pid == profile)
    temps = {}
    for controller in get_controllers.no_lock.no_session(s):
        cid = controller.id
        try:
            temps[cid] = set_points.filter(
                TempSetPoint.cid == cid).one().temperature
        except:
            if use_default:
                temps[cid] = controller.default_temp
    return temps

@with_oven_control_lock
@_sql.with_session
def add_profile(s, name, **kw):
    profile = TempProfile(name=name, **kw)
    s.add(profile)
    return profile

@with_oven_control_lock
@_sql.with_session
def set_profile_temps(s, profile, temps, ignore_error=True):
    if isinstance(profile, TempProfile):
        profile = profile.id
    temp_sets = []
    for cid, temp in temps.items():
        try:
            controller = cid
            temp = to_finite(temp)
        except:
            if not ignore_error:
                return False
            continue
        temp_sets.append((controller, temp))
    for controller, temp in temp_sets:
        s.query(TempSetPoint).filter(TempSetPoint.cid == controller,
                                     TempSetPoint.pid == profile).delete()
        s.add(TempSetPoint(cid=controller, pid=profile, temperature=temp))
    _clean_setpoint(s)
    return True

@with_oven_control_lock
@_sql.with_session
def remove_profile(s, profile):
    try:
        if not isinstance(profile, TempProfile):
            profile = get_profile.no_lock.no_session(profile)
    except:
        return False
    s.delete(profile)
    _clean_setpoint(s)
    return True
