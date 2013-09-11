set(BEC5_FILES
  __init__.py
  models.py
  scripts.py
  server.py
  static/room_temp/js/room-temp.js
  tests.py
  urls.py
  utils.py
  views.py)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()
