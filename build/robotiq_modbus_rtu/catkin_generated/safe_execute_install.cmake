execute_process(COMMAND "/home/gailey_da/catkin_ws_mp/build/robotiq_modbus_rtu/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/gailey_da/catkin_ws_mp/build/robotiq_modbus_rtu/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
