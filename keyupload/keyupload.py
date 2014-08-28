"""
Copyright 2014 Sven Reissmann <sven@0x80.io>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import logging
import os

import bottle


# hostname and tcp port to listen on
# (only used when running with bottles built-in HTTP server)
HOSTNAME = "127.0.0.1"
PORT = 8899

# display debug logs in the webbrowser
# (only used when running with bottles built-in HTTP server)
DEBUG = True

# absolute path to a logfile on disc
LOGFILE = "/var/log/fffd-keyupload.log"

# This variable is used to validate the input.
# MAC addresses and fastd keys only consist of HEX chars.
HEXCHARS = 'abcdef0123456789'

# path where to write fastd public key files
KEYPATH = "/etc/fastd/fffd-mesh-vpn/peers"

# script to execute in order to reload the fastd service
RELOAD_COMMAND = "sudo /opt/fffd-keyupload/script/reload_fastd.sh"


@bottle.route('/', method='GET')
def keys_upload():
    """ provide the keyupload mechanism at URL /

        A valid URL for key uploads looks like this:
        http://server:port/?mac=<macAddress>&key=<fastdKey>
    """
    remote = bottle.request.get('REMOTE_ADDR')
    params = bottle.request.query

    # check whether all parameters have been provided with the request
    if 'mac' not in params.keys() or 'key' not in params.keys():
        logging.error('Request from %s: Missing parameters.', remote)
        return bottle.HTTPResponse(status=400,
                                   body='Error: Missing parameters.')

    # get parameters and do basic validation on them
    mac = params.get('mac', None)
    key = params.get('key', None)

    if set(mac) - set(HEXCHARS) or len(mac) != 12:
        logging.error('Request from %s: Invalid mac address (mac=%s).', remote, mac)
        return bottle.HTTPResponse(status=400,
                                   body='Error: Invalid MAC address.')

    if set(key) - set(HEXCHARS) or len(key) != 64:
        logging.error('Request from %s: Invalid fastd key (key=%s).', remote, key)
        return bottle.HTTPResponse(status=400,
                                   body='Error: Invalid fastd key.')

    # select the filename for the fastd public key file
    # and check whether it already exists (only for logging)
    filename = os.path.join(KEYPATH, mac)
    updatetype = "Added new"
    if os.path.isfile(filename):
        updatetype = "Updated"

    # add or update the fastd public key
    try:
        f = open(filename, 'w')
    except:
        logging.error('Error while trying to access %s.', filename)
        return bottle.HTTPResponse(status=500)

    f.write('key "' + key + '";\n')
    f.close()

    logging.info('Request from %s: %s fastd key %s for mac address %s.',
                 remote, updatetype, key, mac)

    # reload fastd
    if os.system(RELOAD_COMMAND) != 0:
        logging.error('Error while reloading fastd')

    return bottle.HTTPResponse(status=201,
                               body='Done.')


# Enable logging
#
logging.basicConfig(level=logging.INFO,
                    filename=LOGFILE,
                    format='%(asctime)s %(message)s')

logging.info("fffd-keyupload listening on %s:%s", HOSTNAME, PORT)

# Run the application
#
if __name__ == '__main__':
    bottle.run(host=HOSTNAME,
               port=PORT,
               debug=DEBUG)

else:
    application = bottle.default_app()
