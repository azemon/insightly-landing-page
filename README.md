# Landing Page CGI Script for Insightly #

This Python script processes forms on landing pages, interacting with Insightly and with the person who submits the form. 
When the form is submitted, the module does the following:

1. create an organization, iff it does not already exist
1. update/insert a contact and link to the organization
1. add a note to the contact, indicating which form was submitted
1. notify all Insightly users
1. send a thank-you email to the form submitter (as long as both the message's subject and body are defined)
1. redirect the browser to the thank-you page URL

I am not associated with [Insightly, Inc.](https://www.insightly.com/), other than as a user of their CRM.

## Usage ##

### Installing & Configuring this Script ###

Copy `config-sample.py` to `config.py` and edit it using any text editor (not Microsoft Word!).
Insert your Insightly API key. 
If you want to use [reCAPTCHA](https://www.google.com/recaptcha/), add your reCAPTCHA secret key. 
If you do not want to use reCAPTCHA, set the value to "None" (without the quotation marks).

### Creating HTML Forms ###

**There is a sample HTML form in `forms/SampleForm.html` which you can use as a boilerplate. This form is named "TestForm1" and it uses the form data file `forms/TestForm1.txt` as described in the next section of this document.**

Every HTML form must have at least these four input fields:

* first_name
* last_name
* email
* form_name (hidden field)

A few form field names are mapped to specific Insightly contact attributes.

*Contact*

If a Contact already exists for the email address in the form's email field, the Contact will be updated. Otherwise, a new Contact will be created.

* first_name -> Contact's first name
* last_name -> Contact's last name
* email -> Contact's Email (Work)
* phone -> Contact's Phone (Work)
* website -> Contact's Website (Work)
* You can add any other fields that you wish. They will all be copied into the Contact's Background attribute.

*Organization*

If an Organization exists for the domain in the form's email field, the Contact will be linked to it.
If no Organization exists, one will be created and the Contact will be linked to it.
If the domain of the email address is for a free email account, no organization will be created nor will the contact be linked to an organization.
You can see the list of domains for free email accounts in the file `FreeEmailProviders.py`

* company -> Organization's Name (if company is present)
* the email's domain -> Organization's Name (if company is not present)
* the email's domain -> Organization's Domain

*Note*

* All form fields will also be logged into a Note, attached to the Contact.

#### reCAPTCHA ####

If you put your reCAPTCHA secret key into `config.py` then you must include reCAPTCHA in your forms.
See `forms/SampleFormRecaptcha.html` for an example.

#### Form Validation ####

You can use any Javascript form validation mechanism that you like. See the file `forms/SampleFormValidation.html` for a simple technique.

See `forms/SampleFormRecaptchaValidation.html` for an example that combines both reCAPTCHA and form validation.

### Creating Form Data Files ###

**There is a sample form data file in `forms/TestForm1.txt` which you can use as a boilerplate.**

In the `forms` directory, create a file named `FORM_NAME.txt` ("FORM_NAME" has the contents of the form_name hidden field). 
Put the thank-you page URL, the subject line, and the text of the thank-you email into this file.

You can use these tokens in the subject line and in the message. 

* {first_name} - This will be replaced with the contact's first name, from the first_name field of the form.
* {url} - This will be replaced with the URL that you specify in the "url" line of the data file. You do _not_ need to type the URL multiple times.

## Dependencies ##

Landing-page depends on Insightly's Python SDK, included here as a submodule. See the [Insightly API community discussion](https://support.insight.ly/hc/en-us/community/topics/200257170-Insightly-API)

## License ##

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) 

## Author ##

Art Zemon <art@zemon.name>
