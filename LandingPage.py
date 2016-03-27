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
        1) if it does not exist, create an organization
        2) update/insert a contact and link to the organization
        3) add a note to the contact, indicating which form was submitting
        4) notify all Insightly users
        5) send a thank-you email to the form submitter
        6) redirect the browser to the thank-you page URL
    """

    _insightly = None
    _account_owner = None


    def __init__(self):
        try:
            f = open('apikey.txt', 'r')
            apikey = f.read().rstrip()
            f.close()
        except:
            raise Exception('Missing apikey.txt file')
        self._insightly = Insightly.Insightly(apikey=apikey, debug=False)
        self._account_owner = self._insightly.ownerinfo()


    def do_form(self, form_fields):
        """
        process the form from a landing page.
        If there is a form field named "form_name" then it appears in the Note title

        :param form_fields: dictionary
        :return: None
        """

        # preserve original data (for logging) and pull out some key data
        original_form_fields = form_fields.copy()
        email = form_fields['email']
        del form_fields['email']
        form_name = form_fields['form_name']
        del form_fields['form_name']

        organization = self._get_organization(email)

        contact = self._upsert_contact(email, form_fields, organization)

        note = self._add_note(contact['CONTACT_ID'], form_name, original_form_fields)

        self._notify_users(contact, form_name)

        self._thank_you_email(form_name)

        return contact


    def _add_note(self, contact_id, form_name, original_form_fields):
        """
        add a note to a contact
        :param contact_id:
        :param title:
        :param body:
        :return: note
        """
        title = 'Submitted form ' + form_name + ' at ' + dt.datetime.today().strftime("%m/%d/%Y %I:%M:%S%p %Z")
        kv_pairs = []
        for key in original_form_fields.keys():
            kv_pairs.append('<p>%s: %s</p>' % (key, original_form_fields[key]))
        body = ''.join(kv_pairs)

        object_graph = {
            'TITLE': title,
            'BODY': body,
        }
        return self._insightly.create('CONTACTS', object_graph, id=contact_id, sub_type='NOTES')


    def _get_organization(self, email):
        """
        get an organization from the email domain,
        create it if it does not exist
        :param email: contact's email address
        :return: organization
        """
        (username, domain) = email.split('@')
        organization = self._insightly.search('Organisations', 'email_domain=%s' % domain)

        if 0 == len(organization):
            # organisation does not exist; create it
            object_graph = {
                'ORGANISATION_NAME': domain,
                "CONTACTINFOS": [
                    {
                        "TYPE": "EMAILDOMAIN",
                        "LABEL": "Work",
                        "DETAIL": domain
                    }
                ],
            }
            organization = self._insightly.create('Organisations', object_graph=object_graph)
        else:
            # search returns a list and we want the first element
            organization = organization[0]
        return organization


    def _notify_users(self, contact, form_name):
        """
        notify all Insightly users about the form submissions
        :param contact:
        :param users:
        :return: None
        """
        msg = MIMEText('''Contact %s %s submitted form %s. Be sure to check it out.''' % (contact['FIRST_NAME'], contact['LAST_NAME'], form_name))
        to_list = []
        for u in self._insightly.users:
            to_list.append(u['EMAIL_ADDRESS'])
        msg['From'] = self._account_owner['email']
        msg['To'] = ', '.join(to_list)
        msg['Subject'] = 'Form submission: %s' % form_name
        s = smtplib.SMTP('localhost')
        s.sendmail(msg['From'], to_list, msg.as_string())
        s.quit()


    def _thank_you_email(self, form_name):
        """
        Send a thank-you email to the contact
        """
        return


    def _upsert_contact(self, email, values, organization):
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
            ],
            "LINKS": [
                {
                    "ORGANISATION_ID": organization["ORGANISATION_ID"],
                }
            ],
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
        'form_name': 'TestForm1',
    }
    lp = Landing_Page()
    c = lp.do_form(form_fields)
    print str(c)