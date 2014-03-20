set(BEC5_FILES
  __init__.py
  apps.py
  admin.py
  finder.py
  manage.py
  models.py
  scripts.py
  static/jsmodule/js/array.js
  static/jsmodule/js/bootstrap-datetimepicker.min.js
  static/jsmodule/js/gravatar-directive.js
  static/jsmodule/js/logging.js
  static/jsmodule/js/md5-service.js
  static/jsmodule/js/request.js
  static/jsmodule/js/script-loader.js
  static/jsmodule/js/ui-bootstrap-tpls-0.3.0.min.js
  tests.py
  urls.py
  views.py)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()
