set(BEC5_DBUS_FILES
  __init__.py
  main.py
  oven_ctrl.py
  utils.py)

foreach(file ${BEC5_DBUS_FILES})
  add_bec5_pymodule_file("${file}" becv_dbus)
endforeach()
