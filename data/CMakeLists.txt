configure_file(bec5.ini.in bec5.ini @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/bec5.ini"
  DESTINATION "${UWSGI_INI_PATH}")

configure_file(bec5.conf.in bec5.conf @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/bec5.conf"
  DESTINATION "${SYSTEMD_TMP_PATH}")

configure_file(bec5.service.in bec5.service @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/bec5.service"
  DESTINATION "${SYSTEMD_UNIT_PATH}")

configure_file(bec5-dbus.service.in bec5-dbus.service @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/bec5-dbus.service"
  DESTINATION "${SYSTEMD_UNIT_PATH}")

configure_file(bec5.json.in bec5.json @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/bec5.json"
  DESTINATION "${BEC5_CONFIG_PATH}")

configure_file(org.yyc_arch.becv.service.in org.yyc_arch.becv.service @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/org.yyc_arch.becv.service"
  DESTINATION "${DBUS_SYSTEM_SERVICE_PATH}")

configure_file(org.yyc_arch.becv.conf.in org.yyc_arch.becv.conf @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/org.yyc_arch.becv.conf"
  DESTINATION "${DBUS_SYSTEM_CONF_PATH}")
