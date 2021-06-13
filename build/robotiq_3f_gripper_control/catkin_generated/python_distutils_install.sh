#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/gailey_da/catkin_ws_mp/src/robotiq/robotiq_3f_gripper_control"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/gailey_da/catkin_ws_mp/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/gailey_da/catkin_ws_mp/install/lib/python2.7/dist-packages:/home/gailey_da/catkin_ws_mp/build/robotiq_3f_gripper_control/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/gailey_da/catkin_ws_mp/build/robotiq_3f_gripper_control" \
    "/usr/bin/python2" \
    "/home/gailey_da/catkin_ws_mp/src/robotiq/robotiq_3f_gripper_control/setup.py" \
     \
    build --build-base "/home/gailey_da/catkin_ws_mp/build/robotiq_3f_gripper_control" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/home/gailey_da/catkin_ws_mp/install" --install-scripts="/home/gailey_da/catkin_ws_mp/install/bin"
