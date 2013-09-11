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
    COMMAND cp -if "${_from}" "${_to}"
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

set(BEC5_UTILS_FILES
  becv_utils/__init__.py
  becv_utils/math.py
  becv_utils/misc.py
  becv_utils/network.py
  becv_utils/print_color.py
  becv_utils/signal.py
  becv_utils/thread_helper.py
  )

foreach(file ${BEC5_UTILS_FILES})
  add_bec5_pymodule_file("${file}" becv_utils)
endforeach()

set(BEC5_LOGGER_FILES
  becv_logger/__init__.py
  becv_logger/bin_logger.py
  becv_logger/date_fname.py
  becv_logger/error_logger.py
  becv_logger/logger.py
  becv_logger/record_cache.py
  )

foreach(file ${BEC5_LOGGER_FILES})
  add_bec5_pymodule_file("${file}" becv_logger)
endforeach()

set(BEC5_FILES
  db/.gitignore
  log/.gitignore
  becv/__init__.py
  becv/scripts.py
  becv/settings.py
  becv/settings_sync.py
  becv/urls.py
  becv/views.py
  becv/wsgi.py
  bin/becv-manager
  jsmodule/__init__.py
  jsmodule/admin.py
  jsmodule/finder.py
  jsmodule/manage.py
  jsmodule/models.py
  jsmodule/scripts.py
  jsmodule/static/jsmodule/js/array.js
  jsmodule/static/jsmodule/js/bootstrap-datetimepicker.min.js
  jsmodule/static/jsmodule/js/gravatar-directive.js
  jsmodule/static/jsmodule/js/logging.js
  jsmodule/static/jsmodule/js/md5-service.js
  jsmodule/static/jsmodule/js/request.js
  jsmodule/static/jsmodule/js/script-loader.js
  jsmodule/static/jsmodule/js/ui-bootstrap-tpls-0.3.0.min.js
  jsmodule/tests.py
  jsmodule/urls.py
  jsmodule/views.py
  json_view/__init__.py
  json_view/models.py
  json_view/scripts.py
  json_view/static/json_view/js/log-mgr.js
  json_view/tests.py
  json_view/urls.py
  json_view/utils.py
  json_view/views.py
  jsonify/__init__.py
  jsonify/templatetags/__init__.py
  jsonify/templatetags/jsonify.py
  manage.py
  oven_control/__init__.py
  oven_control/controller.py
  oven_control/models.py
  oven_control/tests.py
  oven_control/urls.py
  oven_control/utils.py
  oven_control/views.py
  popup_form/__init__.py
  popup_form/admin.py
  popup_form/models.py
  popup_form/scripts.py
  popup_form/static/popup_form/html/popup_form.html
  popup_form/static/popup_form/js/popup-form.js
  popup_form/tests.py
  popup_form/views.py
  room_temp/__init__.py
  room_temp/models.py
  room_temp/scripts.py
  room_temp/server.py
  room_temp/static/room_temp/js/room-temp.js
  room_temp/tests.py
  room_temp/urls.py
  room_temp/utils.py
  room_temp/views.py
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
  static/js/plot.js
  templates/base.html
  templates/home.html
  templates/registration/logged_out.html
  templates/registration/login.html
  )

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()

add_custom_target(bec5-static ALL
  COMMAND rm -rf static_root
  COMMAND mkdir -p static_root
  COMMAND /usr/bin/python manage.py collectstatic --noinput --settings=becv.settings_sync
  WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
  DEPENDS bec5-files)
install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/static_root/"
  DESTINATION "${BEC5_PREFIX}/static_root/" USE_SOURCE_PERMISSIONS)

configure_file(data/bec5.ini.in data/bec5.ini)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/data/bec5.ini"
  DESTINATION "${UWSGI_INI_PATH}")

configure_file(data/bec5.conf.in data/bec5.conf)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/data/bec5.conf"
  DESTINATION "${SYSTEMD_TMP_PATH}")

configure_file(data/bec5.service.in data/bec5.service)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/data/bec5.service"
  DESTINATION "${SYSTEMD_UNIT_PATH}")

configure_file(data/bec5-dbus.service.in data/bec5-dbus.service)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/data/bec5-dbus.service"
  DESTINATION "${SYSTEMD_UNIT_PATH}")

configure_file(data/org.yyc-arch.becv.service.in data/org.yyc-arch.becv.service)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/data/org.yyc-arch.becv.service"
  DESTINATION "${DBUS_SYSTEM_SERVICE_PATH}")

configure_file(data/org.yyc-arch.becv.conf.in data/org.yyc-arch.becv.conf)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/data/org.yyc-arch.becv.conf"
  DESTINATION "${DBUS_SYSTEM_CONF_PATH}")
