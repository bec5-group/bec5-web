configure_file(bec5.ini.in bec5.ini)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/bec5.ini"
  DESTINATION "${UWSGI_INI_PATH}")

configure_file(bec5.conf.in bec5.conf)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/bec5.conf"
  DESTINATION "${SYSTEMD_TMP_PATH}")

configure_file(bec5.service.in bec5.service)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/bec5.service"
  DESTINATION "${SYSTEMD_UNIT_PATH}")

configure_file(bec5-dbus.service.in bec5-dbus.service)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/bec5-dbus.service"
  DESTINATION "${SYSTEMD_UNIT_PATH}")

configure_file(org.yyc-arch.becv.service.in org.yyc-arch.becv.service)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/org.yyc-arch.becv.service"
  DESTINATION "${DBUS_SYSTEM_SERVICE_PATH}")

configure_file(org.yyc-arch.becv.conf.in org.yyc-arch.becv.conf)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/org.yyc-arch.becv.conf"
  DESTINATION "${DBUS_SYSTEM_CONF_PATH}")
