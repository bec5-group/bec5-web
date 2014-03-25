set(BEC5_SQL_FILES
  __init__.py
  db.py)

foreach(file ${BEC5_SQL_FILES})
  add_bec5_pymodule_file("${file}" becv_sql)
endforeach()
