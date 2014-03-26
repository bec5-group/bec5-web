set(BEC5_DAEMON_FILES
  __init__.py
  main.py
  logger.py
  oven_ctrl/__init__.py
  oven_ctrl/db.py
  oven_ctrl/iface.py)

foreach(file ${BEC5_DAEMON_FILES})
  add_bec5_pymodule_file("${file}" becv_daemon)
endforeach()
