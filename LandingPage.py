#!/usr/bin/env python
#
# Author: Art Zemon art@hens-teeth.net
# License: This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License http://creativecommons.org/licenses/by-sa/4.0/


import datetime as dt
import smtplib
from email.mime.text import MIMEText
from InsightlyPython import insightly as Insightly


class Landing_Page():
    """
    Support a form on a website landing page. When the form on the page gets submitted, do:
        1) update/insert a contact
        2) add a note to the contact, indicating which form was submitting
        3) notify all Insightly users
        4) send a thank-you email to the form submitter
        5) redirect the browser to the thank-you page URL
    """

    _insightly = None

    def __init__(self):
        try:
            f = open('apikey.txt', 'r')
            apikey = f.read().rstrip()
            f.close()
        except:
            raise Exception('Missing apikey.txt file')
        self._insightly = Insightly.Insightly(apikey=apikey, debug=False)


    def do_form(self, form_fields):
        """
        process the form from a landing page.
        If there is a form field named "form_name" then it appears in the Note title

        :param form_fields: dictionary
        :return: None
        """

        original_form_fields = form_fields.copy()

        # create/update the contact
        email = form_fields['email']
        del form_fields['email']
        if 'form_name' in form_fields:
            form_name = form_fields['form_name']
            del form_fields['form_name']
        else:
            form_name = ''
        contact = self._upsert_contact(email, form_fields)

        # create a note, recording the original form fields
        title = 'Submitted form ' + form_name + ' at ' + dt.datetime.today().strftime("%m/%d/%Y %I:%M:%S%p %Z")
        kv_pairs = []
        for key in original_form_fields.keys():
            kv_pairs.append('<p>%s: %s</p>' % (key, original_form_fields[key]))
        if 0 < len(kv_pairs):
            body = ''.join(kv_pairs)
        else:
            body = None
        note = self._add_note(contact['CONTACT_ID'], title, body)

        self._notify_users(contact)

        return contact

    def _add_note(self, contact_id, title, body):
        """
        add a note to a contact
        :param contact_id:
        :param title:
        :param body:
        :return: note
        """
        object_graph = {
            'TITLE': title,
            'BODY': body,
        }
        return self._insightly.create('CONTACTS', object_graph, id=contact_id, sub_type='NOTES')

    def _notify_users(self, contact):
        """
        notify all Insightly users about the form submissions
        :param contact:
        :param users:
        :return: None
        """
        msg = MIMEText('''There is a new form submission for contact %s %s. Be sure to check it out.''' % (contact['FIRST_NAME'], contact['LAST_NAME']))
        to_list = []
        for u in self._insightly.users:
            to_list.append(u['EMAIL_ADDRESS'])
        msg['From'] = 'art@hens-teeth.net'
        msg['To'] = ', '.join(to_list)
        msg['Subject'] = 'Test notification'
        s = smtplib.SMTP('localhost')
        s.sendmail(msg['From'], to_list, msg.as_string())
        s.quit()


    def _upsert_contact(self, email, values):
        """
        Update and existing contact or Insert a new one
        :param email: unique key for the contact
        :param values: other values for the contact
        :return: contact
        """
        contacts = self._insightly.read('contacts', top=2, filters={'email': email})
        contactinfos = [
                {
                    'TYPE': 'EMAIL',
                    'LABEL': 'Work',
                    'DETAIL': email,
                }
            ]

        if 'phone' in values:
            contactinfos.append({
                'TYPE': 'PHONE',
                'LABEL': 'Work',
                'DETAIL': values['phone']
            })
            del values['phone']

        if 'website' in values:
            contactinfos.append({
                'TYPE': 'WEBSITE',
                'LABEL': 'Work',
                'DETAIL': values['website']
            })
            del values['website']

        object_graph = {
            'FIRST_NAME': values['first_name'],
            'LAST_NAME': values['last_name'],
            'CONTACTINFOS': contactinfos,
            'TAGS': [
                {
                    'TAG_NAME': 'Web Contact',
                }
            ]
        }

        # construct a "background" string of any remaining values
        del values['first_name']
        del values['last_name']
        kv_pairs = []
        for key in values.keys():
            kv_pairs.append('%s: %s' % (key, values[key]))
        if 0 < len(kv_pairs):
            background = '\n'.join(kv_pairs)
        else:
            background = None

        if 1 == len(contacts):
            # the contacts already exists; update it
            contact = contacts[0]
            object_graph['CONTACT_ID'] = contact['CONTACT_ID']
            if background is not None:
                if contact['BACKGROUND'] is not None:
                    object_graph['BACKGROUND'] = contact['BACKGROUND'] + '\n' + background
                else:
                    object_graph['BACKGROUND'] = background
            return self._insightly.update('contacts', object_graph, id=contact['CONTACT_ID'])
        else:
            # either the contact does not exist or there is more than one (ambiguous match) so create a new contact
            object_graph['BACKGROUND'] = background
            return self._insightly.create('contacts', object_graph)


if '__main__' == __name__:
    form_fields = {
        'email': '3art@pigasus.com',
        'first_name': 'Robin',
        'last_name': 'Hood',
        'phone': '636-447-3030',
        'website': 'www.hens-teeth.net',
        'company': "Hen's Teeth Network",
        'comments': 'Can you build a website for me?\nAnd do it quick??',
        'form_name': 'The Test Form',
    }
    lp = Landing_Page()
    c = lp.do_form(form_fields)
    print str(c)
