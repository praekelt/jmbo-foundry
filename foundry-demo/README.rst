Jmbo Demo Foundry Setup
=======================

Getting started with a Foundry App

Prerequisites
-------------

 `sudo apt-get install python-virtualenv mysql-server libmysqlclient-dev`

Installation
------------

From the terminal::

 cd jmbo-demo
 virtualenv --no-site-packages ve && source ve/bin/activate
 python bootstrap.py
 ./bin/buildout -N -c dev.cfg (if it fails with `connection reset by peer` just run it again) #This often take a while, so go ahead and make yourself a cup of coffee


MySql Setup
-----------

If this is a brand new installation of mysql, you'll need to change the config file to make MySql transactional. Follow the steps below::

 sudo vi /etc/mysql/my.cnf
 under [mysqld] add
 default-character-set=utf8
 default-storage-engine=innodb
 sudo /etc/init.d/mysql restart

Create db
---------

from a MySQL shell::

 CREATE database demofoundry;
 GRANT ALL ON demofoundry.* TO 'foundry'@'localhost' IDENTIFIED BY 'demofoundry';
 GRANT ALL ON test_demofoundry.* TO 'foundry'@'localhost' IDENTIFIED BY 'demofoundry';
 FLUSH PRIVILEGES;

Setup Django App
----------------

From the terminal

#. run `./install-app`
#. Create a super user when prompted. This will allow you to login into the admin interface.
#. For a brand new site, don't create sample content.

Running app
-----------

From the terminal

`./bin/foundry runserver`

http://localhost:8000/

http://localhost:8000/admin/ #for admin interface



Foundry App CMS
===============

Admin Interface Stuff
---------------------

#. Preferences

 - Setup General Preferences
 - Setup Registration Preferences
 - Setup Login Preferences

#. Navbars
#. Links
#. Posts
#. Listings


Themeing
--------

Place static content in `/jmbo-demo/static/`. `web` and `basic` are provided for the respective theming requirements. `basic` is the fallback theme to be used.

 - `css/custom.css` #your custom css
 - `images/logo.png` #your own log
