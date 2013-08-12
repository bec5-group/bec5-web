project(bec5-web NONE)
cmake_minimum_required(VERSION 2.8.3)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})

include(CompressJS)
include(CMakePathMacros)
include(CMakeTargetMacros)

if("x${BEC5_PREFIX}" STREQUAL "x")
  set(BEC5_PREFIX "/srv/bec5/")
endif()

if("x${SYSTEMD_UNIT_PATH}" STREQUAL "x")
  set(SYSTEMD_UNIT_PATH "${CMAKE_INSTALL_PREFIX}/lib/systemd/system/")
endif()

function(move_file _from _to)
  cmake_utils_to_abs(_from _to)
  cmake_custom_files_to_target(target "${_to}")
  get_filename_component(path "${_to}" PATH)
  add_custom_command(OUTPUT "${_to}"
    COMMAND mkdir -p "${path}"
    COMMAND cp -i "${_from}" "${_to}"
    DEPENDS "${_from}")
  add_custom_target("${target}" ALL DEPENDS "${_to}")
endfunction()

add_custom_target(bec5-files ALL)

function(add_bec5_file src)
  cmake_utils_to_abs(src)
  cmake_utils_src_to_bin(_bin_path "${src}")
  if("x${src}" MATCHES "\\.js\$")
    compress_js("${src}" "${_bin_path}")
  else()
    move_file("${src}" "${_bin_path}")
  endif()
  file(RELATIVE_PATH rel_path "${CMAKE_SOURCE_DIR}" "${src}")
  cmake_utils_abs_path(install_file "${BEC5_PREFIX}/${rel_path}")
  get_filename_component(install_path "${install_file}" PATH)
  install(FILES "${_bin_path}" DESTINATION "${install_path}")
  cmake_custom_files_to_target(target "${_bin_path}")
  add_dependencies(bec5-files "${target}")
endfunction()

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
  becv_utils/__init__.py
  becv_utils/math.py
  becv_utils/network.py
  becv_utils/print_color.py
  becv_utils/signal.py
  becv_utils/thread_helper.py
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
  logger/__init__.py
  logger/bin_logger.py
  logger/date_fname.py
  logger/error_logger.py
  logger/logger.py
  logger/record_cache.py
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
