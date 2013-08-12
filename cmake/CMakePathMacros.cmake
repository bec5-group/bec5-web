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

include(CMakeArrayMacros)

function(cmake_utils_abs_path var path)
  get_filename_component(abs_path "${path}" ABSOLUTE)
  if("x${abs_path}x" MATCHES "^x//")
    string(SUBSTRING "${abs_path}" 1 -1 abs_path)
  endif()
  set("${var}" "${abs_path}" PARENT_SCOPE)
endfunction()

macro(__cmake_utils_to_abs_foreach)
  if("x${${__cmake_utils_to_abs_path_value}}x" STREQUAL xx)
    return()
  endif()
  cmake_utils_abs_path("${__cmake_utils_to_abs_path_value}"
    "${${__cmake_utils_to_abs_path_value}}")
  set("${__cmake_utils_to_abs_path_value}"
    "${${__cmake_utils_to_abs_path_value}}" PARENT_SCOPE)
endmacro()

function(cmake_utils_to_abs)
  cmake_array_foreach(__cmake_utils_to_abs_path_value
    __cmake_utils_to_abs_foreach)
endfunction()

function(cmake_utils_is_subpath ret_var parent child)
  cmake_utils_to_abs(parent child)
  file(RELATIVE_PATH rel_path "${parent}" "${child}")
  string(REGEX MATCH "^\\.\\./" match "${rel_path}")
  if(match)
    set("${ret_var}" False PARENT_SCOPE)
  else()
    set("${ret_var}" True PARENT_SCOPE)
  endif()
endfunction()

function(__cmake_utils_src_to_bin_with_path out path src_path bin_path)
  cmake_utils_is_subpath(issub "${src_path}" "${path}")
  if(issub)
    file(RELATIVE_PATH rel_path "${src_path}" "${path}")
    cmake_utils_abs_path(path "${bin_path}/${rel_path}")
    set("${out}" "${path}" PARENT_SCOPE)
  endif()
endfunction()

function(cmake_utils_src_to_bin out path)
  set(bin_path)
  __cmake_utils_src_to_bin_with_path(bin_path "${path}"
    "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}")
  if(NOT "x${bin_path}" STREQUAL "x")
    set("${out}" "${bin_path}" PARENT_SCOPE)
    return()
  endif()
  __cmake_utils_src_to_bin_with_path(bin_path "${path}"
    "${PROJECT_SOURCE_DIR}" "${PROJECT_BINARY_DIR}")
  if(NOT "x${bin_path}" STREQUAL "x")
    set("${out}" "${bin_path}" PARENT_SCOPE)
    return()
  endif()
  __cmake_utils_src_to_bin_with_path(bin_path "${path}"
    "${CMAKE_SOURCE_DIR}" "${CMAKE_BINARY_DIR}")
  if(NOT "x${bin_path}" STREQUAL "x")
    set("${out}" "${bin_path}" PARENT_SCOPE)
    return()
  endif()
  set("${out}" "${path}" PARENT_SCOPE)
endfunction()

function(_cmake_utils_std_fname_with_dirs var bin src fname)
  cmake_utils_is_subpath(is_bin "${bin}" "${fname}")
  cmake_utils_is_subpath(is_src "${src}" "${fname}")
  if(is_bin OR is_src)
    if(NOT is_src)
      file(RELATIVE_PATH rel_path "${bin}" "${fname}")
    elseif(NOT is_bin)
      file(RELATIVE_PATH rel_path "${src}" "${fname}")
    else()
      cmake_utils_is_subpath(bin_in_src "${src}" "${bin}")
      if(bin_in_src)
        file(RELATIVE_PATH rel_path "${bin}" "${fname}")
      else()
        file(RELATIVE_PATH rel_path "${src}" "${fname}")
      endif()
    endif()
    set("${var}" "${rel_path}" PARENT_SCOPE)
  else()
    set("${var}" "" PARENT_SCOPE)
  endif()
endfunction()

function(cmake_utils_std_fname var fname)
  cmake_utils_to_abs(fname)
  _cmake_utils_std_fname_with_dirs(cur_rel_path "${CMAKE_CURRENT_BINARY_DIR}"
    "${CMAKE_CURRENT_SOURCE_DIR}" "${fname}")
  if(NOT "x${cur_rel_path}x" STREQUAL "xx")
    set("${var}" "${cur_rel_path}" PARENT_SCOPE)
    return()
  endif()
  _cmake_utils_std_fname_with_dirs(pro_rel_path "${PROJECT_BINARY_DIR}"
    "${PROJECT_SOURCE_DIR}" "${fname}")
  if(NOT "x${pro_rel_path}x" STREQUAL "xx")
    set("${var}" "${pro_rel_path}" PARENT_SCOPE)
    return()
  endif()
  _cmake_utils_std_fname_with_dirs(cmake_rel_path "${CMAKE_BINARY_DIR}"
    "${CMAKE_SOURCE_DIR}" "${fname}")
  if(NOT "x${cmake_rel_path}x" STREQUAL "xx")
    set("${var}" "${cmake_rel_path}" PARENT_SCOPE)
    return()
  endif()
  set("${var}" "${fname}" PARENT_SCOPE)
endfunction()
