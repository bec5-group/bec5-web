set(BEC5_FILES
  __init__.py
  models.py
  scripts.py
  static/json_view/js/log-mgr.js
  tests.py
  urls.py
  utils.py
  views.py)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()
