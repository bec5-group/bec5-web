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

include(CMakePathMacros)

function(_cmake_custom_file_to_target var file)
  cmake_utils_std_fname(std_fname "${file}")
  string(REGEX REPLACE "[^-_.a-zA-Z0-9]" "_" std_fname "${std_fname}")
  string(REGEX REPLACE "_+" "_" std_fname "${std_fname}")
  set("${var}" "${std_fname}" PARENT_SCOPE)
endfunction()

macro(__cmake_custom_files_to_target_foreach)
  cmake_utils_to_abs(__cmake_custom_files_to_target_value)
  string(MD5 fname_md5
    "${__cmake_custom_files_to_target_value}")
  _cmake_custom_file_to_target(fname_target
    "${__cmake_custom_files_to_target_value}")
  set(std_fnames "${std_fnames}${fname_target}-")
  set(md5_sums "${md5_sums}-${fname_md5}")
endmacro()

function(_cmake_custom_files_to_target var filelist)
  set(std_fnames "")
  set(md5_sums "")
  cmake_array_foreach(__cmake_custom_files_to_target_value
    __cmake_custom_files_to_target_foreach "${filelist}")
  string(MD5 md5_sums "${md5_sums}")
  string(SUBSTRING "${md5_sums}" 0 16 md5_sums)
  set("${var}" "${std_fnames}${md5_sums}" PARENT_SCOPE)
endfunction()

function(cmake_custom_files_to_target var)
  cmake_array_slice(filelist 1)
  _cmake_custom_files_to_target(result "${filelist}")
  set("${var}" "${result}" PARENT_SCOPE)
endfunction()
