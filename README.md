Freifunk Fulda - Automatic Keyupload
====================================
This python program is used to allow automatic upload of fastd public keys
from arbitrary freifunk nodes to each of the gateway servers.

Introduction
============
Freifunk Fulda firmware comes with an upload mechanism for fastd public keys,
which was inspired by the gluon-ffm-autokey package. Whenever a Freifunk Fulda
node comes online, it tries to upload its public key to each configured gateway
server using an HTTP request.

This script, which runs on each Freifunk Fulda gateway, provides the webservice
required to make key upload work.

Installation
============
* Clone this repository
* Update configuration at the beginning of the script
* Create logfile (as specified in configuration)
* Allow webserver user to write to key directory
* Add webserver configuration

Sample Webserver configuration
==============================
Run the python program as wsgi application using this configuration.

 <VirtualHost *:80>
       ServerName gwXX.domain.tld
       ServerAdmin admin@domain.tld
       DocumentRoot /var/www/gwXX.domain.tld

       WSGIDaemonProcess fffd-keyupload user=www-data group=www-data processes=1 threads=5
       WSGIScriptAlias /upload_key /opt/fffd-keyupload/upload.py

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