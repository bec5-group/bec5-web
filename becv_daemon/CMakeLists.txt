set(BEC5_DAEMON_FILES
  __init__.py
  main.py
  logger.py
  oven_ctrl.py)

foreach(file ${BEC5_DAEMON_FILES})
  add_bec5_pymodule_file("${file}" becv_daemon)
endforeach()
