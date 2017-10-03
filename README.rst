========
 PyPN
========

Abstraction library to send push notifications through APNs, GCM and OneSignal.

.. caution::
   This library only supports Python 3.5

Requirements
============

.. caution::
   Requirements are not installed automatically by pip. The recomended
   dependencies can be found in requirements.txt.

For APNs an @oeegor/apns2-client fork is used, `pypn` branch
::

   https://github.com/alej0varas/apns2-client.git

For GCM @geeknam/python-gcm `develop` branch is used.
::
   
   https://github.com/geeknam/python-gcm.git

For OneSignal `yaosac`.
::

   https://pypi.python.org/pypi/yaosac

Usage
=====

APNS
----
.. code-block:: python

   apns = pypn.Notification(pypn.APNS)
   apns.send(token, data)

Possible values for `token` are:

- A string
- A list of string

Currently sending multiple notifications means iterating over the list
and send one request per user.

GCM
---
.. code-block:: python

   gcm = pypn.Notification(pypn.APNS)
   gcm.send(token, data)


Possible values for `token` are:

- A string

  - `registration_id` or `topic` (just the name, without "/topic/")

- A list of string, `registration_ids`

OneSignal
---------
.. code-block:: python

   ones = pypn.Notification(pypn.OS)
   ones.send(token, data)


Possible values for `token` are:

- A list of OneSignal's `player_id`

You need an App Auth Key and App Id. They can be set as environment
variables 'OS_APP_AUTH_KEY' and 'OS_APP_ID' or assigned to the client
via `user_auth_key` and `app_id` attributes.

Dummy
-----
.. code-block:: python

   dummy = pypn.Notification(pypn.DUMMY)
   dummy.send(token, data)

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

.. code-block:: python

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

- OS_APP_AUTH_KEY
- OS_APP_ID

Debug
=====

Debug is the default value for every provider(you will **not** get
notifications through GCM unless you set debug to false). This can
also be set in the environment:

- APNS_MODE: Possible values are "dev" and "prod"
- GCM_DRY_RUN: Possible values are 0 and 1
- There is no debug mode for OneSignal :(
- Dummy: There is a dummy provider that does nothin

Also logging for the gcm library can be enabled setting `GCM_LOGGING`
environment variable to 1.

Contributing
============

Feel free to open a pull request or issue in GitHub.

Testing
-------
Install requirements

.. code-block:: shell

   pip install -r requirements.txt

Copy and update the environment file

.. code-block:: shell

   cp .env-template .env

**DON'T FORGET TO EDIT .env :)**

Install honcho

.. code-block:: shell

   pip install honcho


Unit
~~~~
.. code-block:: shell

   honcho run python tests.py

Integration
~~~~~~~~~~~
This will send a notification to your devices.

.. code-block:: shell

   honcho run python tests_integration.py
