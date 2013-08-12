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

# Public functions and macros provided by this file
# (See comment of each for more detail):
#     cmake_utils_get_global
#     cmake_utils_set_global
#     cmake_utils_get_unique_name
#     cmake_utils_check_and_set_bool

if(COMMAND cmake_utils_get_global)
  return()
endif()

# cmake_utils_get_global(name ret_var)
#     @name: the name of the global to set
#     @ret_var: the variable to return the value
#
#     This function return a global @name in @ret_var. The global
#     is NOT a variable and can not be access that way.
function(cmake_utils_get_global name var)
  set(property_name "___CMAKE_UTILS_GET_GLOBAL_${name}__")
  get_property(value GLOBAL PROPERTY "${property_name}")
  set("${var}" "${value}" PARENT_SCOPE)
endfunction()

# cmake_utils_set_global(name value)
#     @name: the name of the global to set
#     @value: the value to set
#
#     This function set a global @name to @value. The global
#     is NOT a variable and can not be access that way.
function(cmake_utils_set_global name value)
  set(property_name "___CMAKE_UTILS_GET_GLOBAL_${name}__")
  set_property(GLOBAL PROPERTY "${property_name}" "${value}")
endfunction()

# cmake_utils_get_unique_name(name_hint ret_var)
#     @name_hint: a legal variable and target name acting as a hint for the
#                generated unique name.
#     @ret_var: the variable name to return the generated unique name.
#
#     This function will generate a unique based on the @name_hint and save
#     the result into ret_var. The name can be used as the name of a target,
#     variable, function or macro.
function(cmake_utils_get_unique_name name unique_name)
  set(property_name "___CMAKE_UTILS_UNIQUE_COUNTER_${name}")
  cmake_utils_get_global("${property_name}" current_counter)
  if(NOT current_counter)
    set(current_counter 1)
  endif()
  set(name "cmake_utils_${name}_${current_counter}")
  string(MD5 md5sum_name "${name}")
  set(${unique_name} "${name}_${md5sum_name}" PARENT_SCOPE)
  math(EXPR current_counter "${current_counter} + 1")
  cmake_utils_set_global("${property_name}" "${current_counter}")
endfunction()

# cmake_utils_get_bool(name ret_var)
#     @name: the name of the bool flag to set
#     @ret_var: the variable to return the value
#
#     This function return whether the global bool flag @name is true
#     in @ret_var. The flag is NOT a variable and can not be access that way.
#     See #cmake_utils_set_bool and #cmake_utils_check_and_set_bool for more
#     detail.
function(cmake_utils_get_bool name var)
  set(property_name "___CMAKE_UTILS_CHECK_AND_SET_${name}__")
  cmake_utils_get_global("${property_name}" value)
  if(value)
    set("${var}" 1 PARENT_SCOPE)
  else()
    set("${var}" 0 PARENT_SCOPE)
  endif()
endfunction()

# cmake_utils_set_bool(name value)
#     @name: the name of the bool flag to set
#     @value: bool value to set
#
#     This function set the global bool flag @name to @value.
#     The flag is NOT a variable and can not be access that way.
#     See #cmake_utils_get_bool and #cmake_utils_check_and_set_bool for more
#     detail.
function(cmake_utils_set_bool name value)
  set(property_name "___CMAKE_UTILS_CHECK_AND_SET_${name}__")
  if(value)
    cmake_utils_set_global("${property_name}" 1)
  else()
    cmake_utils_set_global("${property_name}" 0)
  endif()
endfunction()

# cmake_utils_check_and_set_bool(name ret_var)
#     @name: the name of the bool flag to set
#     @ret_var: the variable to return the value
#
#     This function set the global bool flag @name to true and return
#     whether it was true before in @ret_var. The flag is NOT a variable
#     and can not be access that way.
#     See #cmake_utils_set_bool and #cmake_utils_get_bool for more detail.
function(cmake_utils_check_and_set_bool name var)
  cmake_utils_get_bool("${name}" value)
  if(value)
    set("${var}" 1 PARENT_SCOPE)
  else()
    cmake_utils_set_bool("${name}" 1)
    set("${var}" 0 PARENT_SCOPE)
  endif()
endfunction()
