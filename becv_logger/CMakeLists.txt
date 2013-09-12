set(BEC5_LOGGER_FILES
  __init__.py
  bin_logger.py
  date_fname.py
  dbus_proxy.py
  error_logger.py
  log_dir.py
  logger.py
  record_cache.py)

foreach(file ${BEC5_LOGGER_FILES})
  add_bec5_pymodule_file("${file}" becv_logger)
endforeach()
