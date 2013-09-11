set(OVEN_CTRL_FILES
  __init__.py
  controller.py
  utils.py)

foreach(file ${OVEN_CTRL_FILES})
  add_bec5_pymodule_file("${file}" oven_control_service)
endforeach()
