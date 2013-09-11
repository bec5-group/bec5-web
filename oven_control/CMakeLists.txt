set(BEC5_FILES
  __init__.py
  controller.py
  models.py
  tests.py
  urls.py
  views.py)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()
