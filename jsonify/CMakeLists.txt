set(BEC5_FILES
  __init__.py
  templatetags/__init__.py
  templatetags/jsonify.py)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()
