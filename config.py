#!/usr/bin/env python
'''Configure the application. When run directly will output the current configuration.'''

import os

DEBUG = bool(os.environ.get('COVID_DEBUG'))

# API Credentials
auth = {}
auth['PUSHOVER_API_TOKEN'] = os.environ.get('PUSHOVER_API_TOKEN')
auth['PUSHOVER_USER_KEY'] = os.environ.get('PUSHOVER_USER_KEY')
auth['TWILIO_ACCOUNT_SID'] = os.environ.get('TWILIO_ACCOUNT_SID')
auth['TWILIO_AUTH_TOKEN'] = os.environ.get('TWILIO_AUTH_TOKEN')
auth['TWILIO_MESSAGING_SERVICE'] = os.environ.get('TWILIO_MESSAGING_SERVICE')

DB_URI = 'sqlite:///covid.sqlite'
