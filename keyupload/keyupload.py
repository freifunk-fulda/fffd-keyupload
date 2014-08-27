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

import bottle
import os
import logging

# hostname and tcp port to listen on
HOSTNAME = "127.0.0.1"
PORT = 8899

# enable debug logging into the webbrowser
DEBUG = True

# where to write logs to
LOGFILE = "/var/log/fffd-keyupload.log"

# This variable is used to validate the input.
# MAC addresses and fastd keys only consist of HEX chars.
HEXCHARS = 'abcdef0123456789'

# path where to write fastd public key files
KEYPATH = "/etc/fastd/fffd-mesh-vpn/peers"


@bottle.route('/upload_key', method='GET')
def keys_upload():
    remote = bottle.request.get('REMOTE_ADDR')
    params = bottle.request.query

    if 'mac' not in params.keys() or 'key' not in params.keys():
        logging.error('Missing parameters from %s.', remote)
        return bottle.HTTPResponse(status=400,
                                   body='Error: Missing parameters.')

    mac = params.get('mac', None)
    key = params.get('key', None)

    if set(mac) - set(HEXCHARS) or len(mac) != 12:
        logging.error('Invalid mac address (mac=%s) from %s.', mac, remote)
        return bottle.HTTPResponse(status=400,
                                   body='Error: Invalid MAC address.')

    if set(key) - set(HEXCHARS) or len(key) != 64:
        logging.error('Invalid fastd key (key=%s) from %s.', key, remote)
        return bottle.HTTPResponse(status=400,
                                   body='Error: Invalid fastd key.')


    # check for existence of the file
    updatetype = "Added new"
    filename = os.path.join(KEYPATH, mac)
    if os.path.isfile(filename):
        updatetype = "Updated"

    # add or update the key
    try:
        f = open(filename, 'w')

    except:
        logging.error('Error while trying to access %s', filename)
        return bottle.HTTPResponse(status=500)

    f.write('key "' + key + '";\n')
    f.close()

    logging.info('%s fastd key %s for mac address %s from %s.',
                 updatetype, key, mac, remote)

    # reload fastd
    if os.system('pkill -HUP fastd') != 0:
        logging.error('Error while reloading fastd')

    return bottle.HTTPResponse(status=200,
                               body='Done.')


logging.basicConfig(level=logging.INFO,
                    filename=LOGFILE,
                    format='%(asctime)s %(message)s')

logging.info("fffd-keyupload listening on %s:%s", HOSTNAME, PORT)

if __name__ == '__main__':
    bottle.run(host=HOSTNAME,
               port=PORT,
               debug=DEBUG)

else:
    application = bottle.default_app()
