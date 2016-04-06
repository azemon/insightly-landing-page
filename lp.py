#!/usr/bin/env python

# Author: Art Zemon art@zemon.name https://cheerfulcurmudgeon.com/
#
# License: This work is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License http://creativecommons.org/licenses/by-sa/4.0/

# https://hens-teeth.net/cgi-bin/landing-page/lp.py?first_name=Robin&last_name=Hood&email=art@zemon.name&form_name=TestForm1

import cgi
import cgitb
cgitb.enable()

print 'Content-type: text/html'

import os
from LandingPage import Landing_Page

form = cgi.FieldStorage()
form_fields = dict()

for key in form.keys():
    fieldname = str(key)
    value = str(form.getvalue(fieldname))
    form_fields[fieldname] = value

if 0 < len(form_fields):
    form_fields['ip_address'] = cgi.escape(os.environ['REMOTE_ADDR'])
    lp = Landing_Page()
    try:
        url = lp.do_form(form_fields)
        print 'Location: ' + url
        print '\n'
        print 'Redirecting to: ' + url
    except KeyError, e:
        print '\n'
        print '<html><head><title>Error</title></head><body>'
        print '<p>Missing field(s): email, first_name, or last_name</p>'
        print '<p>Press BACK and try again</p>'
        print '</body></html>'
else:
    print '\nError: This script can only be called from a form'
