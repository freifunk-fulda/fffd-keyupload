Freifunk Fulda - Automatic Keyupload
====================================
This python program is used to allow automatic upload of fastd public keys
from arbitrary freifunk nodes to each of the gateway servers.

Introduction
------------
Freifunk Fulda firmware comes with an upload mechanism for fastd public keys,
which was inspired by the gluon-ffm-autokey package. Whenever a Freifunk Fulda
node comes online, it tries to upload its public key to each configured gateway
server using an HTTP request.

This script, which runs on each Freifunk Fulda gateway, provides the webservice
required to make key upload work. Automatic key uploads will use an URL like:
    http://server:port/?mac=<macAddress>&key=<fastdKey>

If valid, the key will be added or updated and fastd gets restarted.

Preconditions
-------------
This program depends on the following packages being installed.
* python >= 2.7
* bottle >= 0.12

Installation
------------
* Clone this repository
* Update configuration section at the beginning of the script
* Permit write access to the logfile specified in configuration
* Allow the user your webserver runs as to write the key directory
* Add sudo permission for webserver user to the reload_fastd.sh script
* Add a virtual host to your webserver configuration

Sample Apache2 configuration
----------------------------
Run the python program as wsgi application using this configuration.

    <VirtualHost *:80>
       ServerName gwXX.domain.tld
       ServerAdmin admin@domain.tld
       DocumentRoot /var/www/gwXX.domain.tld

       WSGIDaemonProcess fffd-keyupload user=www-data group=www-data processes=1 threads=5
       WSGIScriptAlias /upload_key /opt/fffd-keyupload/keyupload/keyupload.py

       <Directory "/var/www/gwXX.domain.tld">
               Options Indexes FollowSymLinks MultiViews
               AllowOverride None
       </Directory>

       <Directory /opt/fffd-keyupload>
               WSGIProcessGroup yourapp
               WSGIApplicationGroup %{GLOBAL}
               Order deny,allow
               Allow from all
       </Directory>

       LogLevel warn
       ErrorLog ${APACHE_LOG_DIR}/error.log
       CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>

Sample sudo configuration
-------------------------
    www-data        ALL = NOPASSWD: /opt/fffd-keyupload/script/reload_fastd.sh
