set(BEC5_FILES
  __init__.py
  scripts.py
  settings_debug.py
  settings.py
  settings_sync.py
  urls.py
  views.py
  wsgi.py)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()
