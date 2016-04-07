#!/usr/bin/env python

# Author: Art Zemon art@zemon.name https://cheerfulcurmudgeon.com/
#
# License: This work is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License http://creativecommons.org/licenses/by-sa/4.0/

# https://hens-teeth.net/cgi-bin/landing-page/lp.py?first_name=Robin&last_name=Hood&email=art@zemon.name&form_name=TestForm1

import cgi
import cgitb
cgitb.enable()

import sys
import os

from config import recaptcha_secretkey
import recaptcha
from LandingPage import Landing_Page

print 'Content-type: text/html'

form = cgi.FieldStorage()
form_fields = dict()

for key in form.keys():
    fieldname = str(key)
    value = str(form.getvalue(fieldname))
    form_fields[fieldname] = value

form_fields['ip_address'] = cgi.escape(os.environ['REMOTE_ADDR'])

if recaptcha_secretkey is not None:
    if 'g-recaptcha-response' in form_fields.keys():
        results = recaptcha.check(form_fields['g-recaptcha-response'], form_fields['ip_address'])
        # don't pass on the reCAPTCHA data; no one else cares about it
        del form_fields['g-recaptcha-response']
    else:
        results = False
    if False == results:
        print '\n'
        print '<html><head><title>Error</title></head><body>'
        print '<p>reCATPCHA failure. Only humans allowed.</p>'
        print '</body></html>'
        sys.exit(0)

if 1 < len(form_fields):
    lp = Landing_Page()
    try:
        url = lp.do_form(form_fields)
        print 'Location: ' + url
        print '\n'
        print 'Redirecting to: ' + url
    except KeyError:
        print '\n'
        print '<html><head><title>Error</title></head><body>'
        print '<p>Missing field(s): email, first_name, or last_name</p>'
        print '<p>Press BACK and try again</p>'
        print '</body></html>'
else:
    print '\nError: This script can only be called from a form'
