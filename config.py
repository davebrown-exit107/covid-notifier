#!/usr/bin/env python
'''Configure the application. When run directly will output the current configuration.'''

import os

DEBUG = bool(os.environ.get('COVID_DEBUG'))

# API Credentials
auth = {}
auth['PUSHOVER_API_TOKEN'] = os.environ.get('COVID_PUSHOVER_API_TOKEN')
auth['PUSHOVER_USER_KEY'] = os.environ.get('COVID_PUSHOVER_USER_KEY')
auth['TWILIO_ACCOUNT_SID'] = os.environ.get('COVID_TWILIO_ACCOUNT_SID')
auth['TWILIO_AUTH_TOKEN'] = os.environ.get('COVID_TWILIO_AUTH_TOKEN')
auth['TWILIO_MESSAGING_SERVICE'] = os.environ.get('COVID_TWILIO_MESSAGING_SERVICE')

if __name__ == '__main__':
    for key, value in os.environ.items():
        if 'FLASK_' in key:
            print(f'{key}: {value}')
        if 'COVID_' in key:
            print(f'{key[6:]}: {value}')
