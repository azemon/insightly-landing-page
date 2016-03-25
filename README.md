Landing Page CGI Script for Insightly
=====================================

This Python script processes forms on landing pages, interacting with Insightly and with the person who submits the form. 
When the form is submitted, the module does the following:

1. update/insert a contact
1. add a note to the contact, indicating which form was submitting
1. notify all Insightly users
1. send a thank-you email to the form submitter
1. redirect the browser to the thank-you page URL

Usage
=====

Put your Insightly API key in a file named `apikey.txt` in the same directory as `LandingPage.py`

Create an HTML form with at least these four input fields:

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

Dependencies
============

Landing-page depends on Insightly's Python SDK, included here as a submodule.

License
=======
This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) 

Author
=====

Art Zemon <art@zemon.name>
