#! /bin/bash

DJANGO_DIR=praekelt

echo "Prepare a clean Ubuntu 12.04 server to serve Jmbo sites"

echo "Installing required Ubuntu packages..."
# Postgres is special. We want only one instance since Ubuntu will happily 
# install different versions side by side.
sudo /etc/init.d/postgresql stop
sudo apt-get remove "postgresql-8.4"
sudo apt-get --no-upgrade install python-virtualenv python-dev \
postgresql-9.1 libjpeg-dev zlib1g-dev build-essential git-core \
memcached supervisor nginx --no-upgrade

echo "Configuring PostgreSQL..."
# xxx: regexes would be better
sudo sed -i "s/local   all             all                                     peer/local   all             all                                     trust/" /etc/postgresql/9.1/main/
sudo /etc/init.d/postgresql start

echo "Setting up the www-data user..."
sudo mkdir /var/www
sudo mkdir /var/www/.buildout
sudo mkdir /var/www/.buildout/eggs
sudo su -c 'echo "[buildout]" > /var/www/.buildout/default.cfg'
sudo su -c 'echo "eggs-directory = /var/www/.buildout/eggs" >> /var/www/.buildout/default.cfg'
sudo chown -R www-data:www-data /var/www
sudo usermod www-data -s /bin/bash

echo "Setting up the Django directory..."
sudo mkdir /var/${DJANGO_DIR}
sudo chown -R www-data:www-data /var/praekelt

echo ""
echo "All done! You probably want to run the setup-app.sh script now."
