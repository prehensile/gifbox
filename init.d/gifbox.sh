#! /bin/sh
### BEGIN INIT INFO
# Provides:          gifbox
# Required-Start:    $all
# Required-Stop:     
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Manage gifbox
### END INIT INFO

case "$1" in
  start)
    log_begin_msg "Starting gifbox"
    sudo python /home/pi/gifbox/gifbox.py
    log_end_msg $?
    exit 0
    ;;
  stop)
    log_begin_msg "Stopping gifbox"
    # TODO: stash the pid somewhere. this is a little... nuclear
    sudo killall -9 python
    log_end_msg $?
    exit 0
    ;;
  *)
    echo "Usage: /etc/init.d/gifbox {start|stop}"
    exit 1
    ;;
esac
