set(BEC5_FILES
  base.html
  home.html
  registration/logged_out.html
  registration/login.html)

foreach(file ${BEC5_FILES})
  add_bec5_file("${file}")
endforeach()
