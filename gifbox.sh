case "$1" in
  start)
    cd /home/pi/gifbox
    # selfupdate
    git pull
    # activate virtualenv
    source .venv/bin/activate
    # start main & save pid
    sudo python gifbox.py &
    echo $! >~/.gifbox/pid
    exit 0
    ;;
  stop)
    sudo kill -TERM $(cat ~/.gifbox/pid)
    exit 0
    ;;
  *)
    echo "Usage: /etc/init.d/gifbox {start|stop}"
    exit 1
    ;;
esac