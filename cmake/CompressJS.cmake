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

set(compress_script "${CMAKE_CURRENT_LIST_DIR}/compress-js.sh")

function(compress_js _from _to)
  cmake_utils_to_abs(_from _to)
  cmake_custom_files_to_target(target "${_to}")
  get_filename_component(path "${_to}" PATH)
  add_custom_command(OUTPUT "${_to}"
    COMMAND mkdir -p "${path}"
    COMMAND "${compress_script}" "${_from}" "${_to}"
    DEPENDS "${_from}")
  add_custom_target("${target}" ALL DEPENDS "${_to}")
endfunction()
