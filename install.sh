# gifbox's cache folder
mkdir ~/.gifbox

# install dependencies
sudo apt-get install gifsicle fbi python-pip -y

# create & provision a virtualenv
sudo pip install virtualenv
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt

# install splash screen 
sudo ln -s init.d/asplash.sh /etc/init.d/asplash.sh 
sudo update-rc.d asplash.sh defaults

# link init.d script
sudo ln -s init.d/gifbox.sh /etc/init.d/gifbox.sh
sudo update-rc.d gifbox.sh defaults