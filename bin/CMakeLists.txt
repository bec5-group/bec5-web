set(BEC5_FILES
  becv-manager)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()
