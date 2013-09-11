set(BEC5_FILES
  __init__.py
  admin.py
  models.py
  scripts.py
  static/popup_form/html/popup_form.html
  static/popup_form/js/popup-form.js
  tests.py
  views.py)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()
