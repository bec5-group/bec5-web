project(bec5-web NONE)
cmake_minimum_required(VERSION 2.8.3)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})

include(CompressJS)
include(CMakePathMacros)
include(CMakeTargetMacros)
find_package(PythonLibrary REQUIRED)

if("x${BEC5_UWSGI_USER}" STREQUAL "x")
  set(BEC5_UWSGI_USER http)
endif()

if("x${BEC5_UWSGI_GROUP}" STREQUAL "x")
  set(BEC5_UWSGI_GROUP http)
endif()

if("x${BEC5_PREFIX}" STREQUAL "x")
  set(BEC5_PREFIX "/srv/bec5/")
endif()

if("x${SYSTEMD_UNIT_PATH}" STREQUAL "x")
  set(SYSTEMD_UNIT_PATH "${CMAKE_INSTALL_PREFIX}/lib/systemd/system/")
endif()

if("x${SYSTEMD_TMP_PATH}" STREQUAL "x")
  set(SYSTEMD_TMP_PATH "${CMAKE_INSTALL_PREFIX}/lib/tmpfiles.d/")
endif()

if("x${UWSGI_INI_PATH}" STREQUAL "x")
  set(UWSGI_INI_PATH "/etc/uwsgi/")
endif()

if("x${UWSGI_SOCK_PATH}" STREQUAL "x")
  set(UWSGI_SOCK_PATH "/run/uwsgi/bec5/")
endif()

if("x${DBUS_SYSTEM_SERVICE_PATH}" STREQUAL "x")
  set(DBUS_SYSTEM_SERVICE_PATH
    "${CMAKE_INSTALL_PREFIX}/share/dbus-1/system-services/")
endif()

if("x${DBUS_SYSTEM_CONF_PATH}" STREQUAL "x")
  set(DBUS_SYSTEM_CONF_PATH "/etc/dbus-1/system.d")
endif()

function(move_file _from _to)
  cmake_utils_to_abs(_from _to)
  cmake_custom_files_to_target(target "${_to}")
  get_filename_component(path "${_to}" PATH)
  add_custom_command(OUTPUT "${_to}"
    COMMAND mkdir -p "${path}"
    COMMAND cp -vf "${_from}" "${_to}"
    DEPENDS "${_from}")
  add_custom_target("${target}" ALL DEPENDS "${_to}")
endfunction()

add_custom_target(bec5-files ALL)

function(add_bec5_file src)
  cmake_utils_to_abs(src)
  file(RELATIVE_PATH rel_path "${CMAKE_SOURCE_DIR}" "${src}")
  message(STATUS "Adding ${rel_path}.")
  cmake_utils_src_to_bin(_bin_path "${src}")
  if("x${src}" MATCHES "\\.js\$")
    compress_js("${src}" "${_bin_path}")
  else()
    move_file("${src}" "${_bin_path}")
  endif()

  cmake_custom_files_to_target(target "${_bin_path}")
  add_dependencies(bec5-files "${target}")

  if("${rel_path}" MATCHES "^static/" OR "${rel_path}" MATCHES "/static/" )
    return()
  endif()
  cmake_utils_abs_path(install_file "${BEC5_PREFIX}/${rel_path}")
  get_filename_component(install_path "${install_file}" PATH)
  install(FILES "${_bin_path}" DESTINATION "${install_path}")
endfunction()

function(add_bec5_pymodule_file src module)
  cmake_utils_to_abs(src)
  file(RELATIVE_PATH rel_path "${CMAKE_SOURCE_DIR}" "${src}")
  message(STATUS "Adding ${rel_path}.")
  cmake_utils_src_to_bin(_bin_path "${src}")
  move_file("${src}" "${_bin_path}")
  install(FILES "${_bin_path}"
    DESTINATION "${PYTHON_SITE_PACKAGES_DIR}/${module}")
  cmake_custom_files_to_target(target "${_bin_path}")
  add_dependencies(bec5-files "${target}")
endfunction()

add_subdirectory(becv)
add_subdirectory(becv_logger)
add_subdirectory(becv_utils)
add_subdirectory(bin)
add_subdirectory(data)
add_subdirectory(jsmodule)
add_subdirectory(json_view)
add_subdirectory(jsonify)
add_subdirectory(oven_control)
add_subdirectory(oven_control_service)
add_subdirectory(popup_form)
add_subdirectory(room_temp)
add_subdirectory(templates)

set(BEC5_FILES
  db/.gitignore
  log/.gitignore
  manage.py

  # cannot put cmake file in static/ otherwise ./manage.py collectstatic will
  # collect them
  static/css/bootstrap-datetimepicker.min.css
  static/css/home.css
  static/css/login_out.css
  static/img/favicon.png
  static/img/favicon.svg
  static/img/favicon2.png
  static/img/favicon2.svg
  static/img/loading.gif
  static/js/home.js
  static/js/login.js
  static/js/plot.js)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()

add_custom_target(bec5-static ALL
  COMMAND rm -rf static_root
  COMMAND mkdir -p static_root
  COMMAND /usr/bin/python manage.py collectstatic
  --noinput --settings=becv.settings_sync
  WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
  DEPENDS bec5-files)
install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/static_root/"
  DESTINATION "${BEC5_PREFIX}/static_root/" USE_SOURCE_PERMISSIONS)
