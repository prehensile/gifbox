# gifbox's cache folder
mkdir ~/.gifbox

# install dependencies
apt-get install gifsicle fbi python-pip -y
pip install -r requirements.txt

# install splash screen 
ln -s /home/pi/gifbox/init.d/asplash.sh /etc/init.d/asplash.sh 
insserv /etc/init.d/asplash.sh

# link init.d script
ln -s /home/pi/gifbox/init.d/gifbox.sh /etc/init.d/gifbox.sh
update-rc.d gifbox.sh defaults
