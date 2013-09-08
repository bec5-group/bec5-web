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

class ControllerManager(object):
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
