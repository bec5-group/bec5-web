set(BEC5_UTILS_FILES
  __init__.py
  apps.py
  dbus.py
  gsignal.py
  math.py
  misc.py
  network.py
  print_color.py
  signal.py
  thread_helper.py)

foreach(file ${BEC5_UTILS_FILES})
  add_bec5_pymodule_file("${file}" becv_utils)
endforeach()
