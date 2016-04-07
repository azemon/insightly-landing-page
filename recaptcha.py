# Author: Art Zemon art@zemon.name https://cheerfulcurmudgeon.com/
#
# License: This work is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License http://creativecommons.org/licenses/by-sa/4.0/

import json
try:
    import requests
except:
    # no system version of Requests so use local copy
    import os
    import sys
    parent_dir = os.path.abspath(os.path.dirname(__file__))
    vendor_dir = os.path.join(parent_dir, 'requests')
    sys.path.append(vendor_dir)
    import requests

from config import recaptcha_secretkey

apiurl = 'https://www.google.com/recaptcha/api/siteverify'

def check(recaptcha_response, remoteip):
    data = {
        'secret': recaptcha_secretkey,
        'response': recaptcha_response,
        'remoteip': remoteip,
    }

    print 'data = ', data

    r = requests.post(apiurl, data)
    response = json.loads(r.content)
    print 'response = ', response
    return response['success']