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
    DESTDIR_ARG="--root=$DESTDIR"
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/vagrant/ros_ws/src/baxter/gazebo_ros_pkgs/gazebo_plugins"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/vagrant/ros_ws/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/vagrant/ros_ws/install/lib/python2.7/dist-packages:/home/vagrant/ros_ws/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/vagrant/ros_ws/build" \
    "/usr/bin/python2" \
    "/home/vagrant/ros_ws/src/baxter/gazebo_ros_pkgs/gazebo_plugins/setup.py" \
    build --build-base "/home/vagrant/ros_ws/build/baxter/gazebo_ros_pkgs/gazebo_plugins" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/vagrant/ros_ws/install" --install-scripts="/home/vagrant/ros_ws/install/bin"
