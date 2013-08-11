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

"""
Functions to deal with infinity. Mainly because python's json module output
Infinity and NaN which may not be recognized by javascript's JSON parser.
"""

import math

def to_finite(s):
    val = float(s)
    if math.isnan(val) or math.isinf(val):
        raise ValueError(val)
    return val

def fix_non_finite(s):
    try:
        return to_finite(s)
    except:
        return 0.0
