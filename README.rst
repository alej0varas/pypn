========
 PyPN
========

Abstraction library to send push notifications through APNs and GCM.

.. caution::
   This library is in early development state.

.. caution::
   This library only supports Python 3.5

Requirements
============

.. caution::
   Requirements are not installed automatically by pip you can find them in `requirements.txt`

For APNs an @oeegor/apns2-client fork is used, `pypn` branch
::

   https://github.com/alej0varas/apns2-client.git

For GCM @geeknam/python-gcm `develop` branch is used.
::
   
   https://github.com/geeknam/python-gcm.git

For OneSignal @gettalent/one-signal-python-sdk, `strip` branch is used.
::

   https://github.com/alej0varas/one-signal-python-sdk.git

Usage
=====

APNS
----
::

   apns = pypn.Notification(pyvenv.APNS)
   apns.send(token, data)

Possible values for `token` are:

- A string
- A list of string

Currently sending multiple notifications means iterating over the list
and send one request per user.

GCM
---
::

   gcm= pypn.Notification(pyvenv.APNS)
   gcm.send(token, data)


Possible values for `token` are:

- A string

  - `registration_id` or `topic` (just the name, without "/topic/")

- A list of string, `registration_ids`

OneSignal
---------
::

   ones = pypn.Notification(pyvenv.OS)
   ones.send(token, data)


Possible values for `token` are:

- A of OneSignal's `player_id`


PyPN takes care of using the right method to send notifications for
based on the token.

Data
====

PyPN has been built as a layer in between a "back-end"(I'm working
on a Django application to handle data) and the existing push
notification libraries. That means notifications are defined including
all the required fields for each provider. This data is then passed to
PyPN together with the provider "name".

Example data
------------

Not every field value is set.
::

   data = {
      # Common fields
      'body': '1, 2, 3, ... push sucks!'
      'sound': 'default',
      'priority': 'high',
      'title': 'Hello, World!',

      # APNs aps
      'apns_badge': 69,
      'apns_content_available': 1,
      'apns_category': '',
      'apns_mutable_content': True,
      # APNs alert
      'apns_alert_title_loc_key': '',
      'apns_alert_title_loc_args': '',
      'apns_alert_loc_key': '',
      'apns_alert_loc_args': '',
      'apns_alert_action_loc_key': '',
      'apns_alert_launch_image': '',
      # APNs data
      'apns_custom': {'custom': 'values'},
  
      # GCM data
      'gcm_data': {'custom': 'values'},
      # GCM notification 
      'gcm_notification_icon': '',
      'gcm_notification_tag': '',
      'gcm_notification_color': '',
      'gcm_notification_click_action': '',
      'gcm_notification_body_loc_key': '',
      'gcm_notification_body_loc_args': '',
      'gcm_notification_title_loc_key': '',
      'gcm_notification_title_loc_args': '',
      # GCM options
      'gcm_option_collapse_key': '',
      'gcm_option_content_available': '',
      'gcm_option_delay_while_idle': '',
      'gcm_option_time_to_live': 40320,
      'gcm_option_restricted_package_name': '',
   }

Credentials
===========

Credentials are expected to be in placed in the environment.

For APNs the path to the .pem certificate and the pass-phrase if any:

- APNS_CERT_FILE
- APNS_CERT_PASSWORD

For GCM the server key:

- GCM_SERVER_KEY

For OneSignal the application id and the API key:

- OS_APP_ID
- OS_API_KEY

Debug
=====

Debug is the default value for every provider(you will **not** get
notifications through GCM unless you set debug to false). This can
also be set in the environment:

- APNS_MODE: Possible values are "dev" and "prod"
- GCM_DRY_RUN: Possible values are 0 and 1

Also logging for the gcm library can be enabled setting `GCM_LOGGING`
environment variable to 1.

Contributing
============

Feel free to open a pull request or issue in GitHub.

Testing
-------
Install requirements
::

   pip install -r requirements.txt

Copy and update the environment file
::

   cp .env-template .env

**DON'T FORGET TO EDIT .env :)**

Install honcho
::

   pip install honcho


Unit
~~~~
::

   honcho run python tests.py

Integration
~~~~~~~~~~~
This will send a notification to your devices
::

   honcho run python tests_integration.py
