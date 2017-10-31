case "$1" in
  start)
    # cd /home/pi/gifbox
    # selfupdate
    git pull
    # start main & save pid
    python gifbox.py &
    echo $! >~/.gifbox/pid
    exit 0
    ;;
  stop)
    kill -TERM $(cat ~/.gifbox/pid)
    rm ~/.gifbox/pid
    exit 0
    ;;
  *)
    echo "Usage: /etc/init.d/gifbox {start|stop}"
    exit 1
    ;;
esac
