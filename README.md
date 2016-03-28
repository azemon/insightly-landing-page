# Landing Page CGI Script for Insightly #

This Python script processes forms on landing pages, interacting with Insightly and with the person who submits the form. 
When the form is submitted, the module does the following:

1. create an organization, iff it does not already exist
1. update/insert a contact and link to the organization
1. add a note to the contact, indicating which form was submitted
1. notify all Insightly users
1. send a thank-you email to the form submitter
1. redirect the browser to the thank-you page URL

I am not associated with [Insightly, Inc.](https://www.insightly.com/), other than as a user of their CRM.

## Usage ##

### Installing & Configuring this Script ###

Put your Insightly API key in a file named `apikey.txt` in the same directory as `LandingPage.py`

### Creating HTML Forms ###

Every HTML form must have at least these four input fields:

* first_name
* last_name
* email
* form_name (hidden field)

You can add any other fields that you wish. A few form field names are mapped to specific Insightly contact attributes. 
Everything else is copied into the Background attribute.

* first_name -> Contact's first name
* last_name -> Contact's last name
* email -> Contact's Email (Work)
* phone -> Contact's Phone (Work)
* website -> Contact's Website (Work)
* the email's domain -> Organization's Name
* the email's domain -> Organization's Domain

### Creating Form Data Files ###

In the `forms` directory, create a file named `FORM_NAME.txt` (same as the contents of the form_name hidden field). 
Put the thank-you page URL and the text of the thank-you email into this file. Here is a sample form data file:

```python
url = 'https://hens-teeth.net/thank-you/magnificent.html'

subject = 'Here is Your Magnificent Ebook'

message = '''
Hello {first_name},

Thank you for requesting our magnificent ebook.
You can download it from {url}

If you have any questions, I am here to help you, 24x7.
As they say in the biz, "here's a quarter; call someone who cares."

Sincerely,
A. Nony Mouse, CMO
Rude Company, Inc.
'''
```

## Dependencies ##

Landing-page depends on Insightly's Python SDK, included here as a submodule. See the [Insightly API community discussion](https://support.insight.ly/hc/en-us/community/topics/200257170-Insightly-API)

## License ##

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) 

## Author ##

Art Zemon <art@zemon.name>
