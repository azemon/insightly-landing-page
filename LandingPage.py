#!/usr/bin/env python
#
# Author: Art Zemon art@zemon.name https://cheerfulcurmudgeon.com/
#
# License: This work is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License http://creativecommons.org/licenses/by-sa/4.0/

import datetime as dt
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from InsightlyPython import insightly as Insightly
from FreeEmailProviders import FreeEmailProviders

from config import insightly_apikey


class Landing_Page:
    """
    Support a form on a website landing page. When the form on the page gets submitted, do:
        1) if it does not exist, create an organization
        2) update/insert a contact and link to the organization
        3) add a note to the contact, indicating which form was submitting
        4) notify all Insightly users
        5) send a thank-you email to the form submitter, and BCC it into Insightly (as long as both the subject line
           and body are defined)
        6) return the URL of the thank-you page
    """

    _insightly = None
    _account_owner = None
    _bcc = None

    _form_data_directory = 'forms'
    _form_data = None # will be a dict with elements: url, subject, message

    # debugging flags
    _no_notification_mail = False


    def __init__(self, nomail=False):
        self._insightly = Insightly.Insightly(apikey=insightly_apikey, debug=False)
        self._account_owner = self._insightly.ownerinfo()
        self._bcc = self._account_owner['email_dropbox']
        self._no_notification_mail = nomail


    def do_form(self, form_fields):
        """
        process the form from a landing page.
        If there is a form field named "form_name" then it appears in the Note title

        :param form_fields: dictionary. Required elements: email, first_name, last_name
        :return: URL of the thank-you page
        """

        if 'email' not in form_fields or 'first_name' not in form_fields or 'last_name' not in form_fields:
            raise KeyError('Required fields: email, first_name, last_name')

        # preserve original data (for logging) and pull out some key data
        original_form_fields = form_fields.copy()
        email = form_fields['email']
        del form_fields['email']
        form_name = form_fields['form_name']
        del form_fields['form_name']

        self._read_form_data(form_name)

        # do not set up organizations for free email accounts
        (username, domain) = email.split('@')
        if FreeEmailProviders.is_free(domain):
            organization = None
        else:
            organization = self._get_organization(email, form_fields)

        contact = self._upsert_contact(email, form_fields, organization)

        note = self._add_note(contact['CONTACT_ID'], form_name, original_form_fields)

        self._notify_users(contact, form_name)

        self._send_thank_you_email(contact, email)

        return self._form_data['url']


    def _add_note(self, contact_id, form_name, original_form_fields):
        """
        add a note to a contact
        :param contact_id:
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


    def _get_organization(self, email, form_fields):
        """
        get an organization from the email domain,
        create it if it does not exist
        :param email: contact's email address
        :return: organization
        """
        (username, domain) = email.split('@')
        organization = self._insightly.search('Organisations', 'email_domain={domain}'.format(domain=domain))

        if 0 == len(organization):
            # organisation does not exist; create it
            try:
                org_name = form_fields['company']
            except:
                org_name = domain
            object_graph = {
                'ORGANISATION_NAME': org_name,
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
        msg = MIMEText(u'Contact {first} {last} submitted form {form}.'.format(first=contact['FIRST_NAME'],
                                                                               last=contact['LAST_NAME'],
                                                                               form=form_name),
                       'plain', 'utf-8')
        to_list = []
        for u in self._insightly.users:
            to_list.append(u['EMAIL_ADDRESS'])

        # the printable name is UTF-8 but the <email@address> is ASCII
        from_name = Header(self._account_owner['name'], 'utf-8')
        msg['From'] = '{name} <{email}>'.format(name=from_name, email=self._account_owner['email'])

        msg['To'] = ', '.join(to_list)
        subject = \
            Header(u'Form {form_name} submitted by {first_name} {last_name}'.format(form_name=form_name,
                                                                                    first_name=contact['FIRST_NAME'],
                                                                                    last_name=contact['LAST_NAME']),
                   'utf-8')
        msg['Subject'] = subject
        s = smtplib.SMTP('localhost')
        if not self._no_notification_mail:
            s.sendmail(msg['From'], to_list, msg.as_string())
        s.quit()


    def _read_form_data(self, form_name):
        # get data about the form
        filename = '{directory}/{basename}.txt'.format(directory=self._form_data_directory, basename=form_name)
        with open(filename, 'r') as f:
            raw_form_data = f.read()
        try:
            exec raw_form_data
            # url contains the thank-you page URL
            # subject contains the email subject template
            # message contains the email message template
            self._form_data = {
                'url': unicode(url.strip()),
                'subject': unicode(subject),
                'message': unicode(message),
            }
        except SyntaxError, e:
            # todo: nice message to Insightly account owner about syntax error and don't fail to redirect to thank-you page
            raise
        except NameError, e:
            # todo: nice message to Insightly user about missing line and don't fail to redirect
            raise
        return


    def _send_thank_you_email(self, contact, contact_email):
        """
        Send a thank-you email to the contact
        :param contact_email:
        :param contact:
        """

        if self._form_data['message'] is None or self._form_data['subject'] is None:
            return

        message = self._form_data['message'].strip().format(first_name=contact['FIRST_NAME'],
                                                            url=self._form_data['url'])
        msg = MIMEText(message, 'plain', 'utf-8')
        to_list = [contact_email]
        if self._bcc is not None:
            to_list.append(self._bcc)

        # the printable name is UTF-8 but the <email@address> is ASCII
        from_name = Header(self._account_owner['name'], 'utf-8')
        msg['From'] = '{name} <{email}>'.format(name=from_name, email=self._account_owner['email'])

        # the printable name is UTF-8 but the <email@address> is ASCII
        to_name = Header(u'{first_name} {last_name}'.format(first_name=contact['FIRST_NAME'],
                                                            last_name=contact['LAST_NAME']),
                         'utf-8')
        msg['To'] = '{name} <{address}>'.format(name=to_name, address=contact_email)

        msg['Subject'] = self._form_data['subject'].strip().format(first_name=contact['FIRST_NAME'])
        s = smtplib.SMTP('localhost')
        s.sendmail(msg['From'], to_list, msg.as_string())
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
        }

        if organization is not None:
            object_graph['LINKS'] = [
                {
                    "ORGANISATION_ID": organization["ORGANISATION_ID"],
                }
            ]

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
        'email': u'art@zemon.name',
        'first_name': u'R\u00f6bin',
        'last_name': u'Hood',
        'phone': u'636-447-3030',
        'website': u'www.hens-teeth.net',
        'company': u"Zemon Manufacturing",
        'comments': u'Can you build a website for me?\nAnd do it quick??',
        'form_name': u'TestForm1',
    }
    lp = Landing_Page(nomail=True)
    url = lp.do_form(form_fields)
    print u'Redirect to {url}'.format(url=url)
