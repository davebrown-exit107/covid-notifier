'''Utility that pulls down statewide Coronavirus results and alerts you to your county's numbers.'''
from itertools import accumulate
import os
from urllib.parse import quote

import requests
from twilio.rest import Client

DEBUG = bool(os.environ.get('COVID_DEBUG'))

# API Credentials
PUSHOVER_API_TOKEN = os.environ.get('PUSHOVER_API_TOKEN')
PUSHOVER_USER_KEY = os.environ.get('PUSHOVER_USER_KEY')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_MESSAGING_SERVICE = os.environ.get('TWILIO_MESSAGING_SERVICE')

# Import other vars
from sensitive import phone_numbers, counties_monitored, statewide

# Build the Twilio client
if not DEBUG:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Setup some constants for our query
BASE_URL = 'https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/0/query?'
RET_FORMAT = 'json'
WHERE_QUERY = 'Total <> 0'
RETURN_GEOMETRY = 'false'
SPATIAL_REL = 'esriSpatialRelIntersects'
OUT_FIELDS = 'orderByFields=NewCases desc,NAMELABEL asc&outSR=102100'
RESULT_OFFSET = '0'
RESULT_RECORD_COUNT = '56'
RESULT_TYPE = 'standard'
CACHE_HINT = 'true'

# Fill in the params from the above constants
query_options = [
    "f={}".format(quote(RET_FORMAT)),
    "&where={}".format(quote(WHERE_QUERY)),
    "&returnGeometry={}".format(quote(RETURN_GEOMETRY)),
    "&spatialRel={}".format(quote(SPATIAL_REL)),
    "&outFields=*&{}".format(quote(OUT_FIELDS)),
    "&resultOffset={}".format(quote(RESULT_OFFSET)),
    "&resultRecordCount={}".format(quote(RESULT_RECORD_COUNT)),
    "&resultType={}".format(quote(RESULT_TYPE)),
    "&cacheHint={}".format(quote(CACHE_HINT))
    ]

FULL_URL = ''.join([BASE_URL, ''.join(query_options)])

# Run the query
results = requests.get(FULL_URL).json()

#######################################
# Statewide Statistics
#######################################
    # Output statewide statistics
if statewide:
    new_cases = sum(entry['attributes']['NewCases'] for entry in results['features'])
    total_active = sum(entry['attributes']['TotalActive'] for entry in results['features'])
    hospitalized = sum(entry['attributes']['HospitalizationCount'] for entry in results['features'])
    cumulative_total = sum(entry['attributes']['Total'] for entry in results['features'])
    cumulative_recovered = sum(entry['attributes']['TotalRecovered'] for entry in results['features'])
    cumulative_deaths = sum(entry['attributes']['TotalDeaths'] for entry in results['features'])

    notification = [
        "Montana",
        f"New Cases: {new_cases: >15}",
        f"Total Active: {total_active: >12}",
        f"Hospitalized: {hospitalized: >12}",
        f"Total Cases: {cumulative_total: >13}",
        f"Total Recovered: {cumulative_recovered: >9}",
        f"Total Deaths: {cumulative_deaths: >12}",
        ]

    if DEBUG:
        print('\n'.join(notification))
        print()
    else:
        # Build a message per county. Stolen from the first todo on Twilio's site.
        for phone_number in phone_numbers:
            message = client.messages.create(
                body='\n'.join(notification),
                messaging_service_sid=TWILIO_MESSAGING_SERVICE,
                to=phone_number
                )

#            # Pushover message sender
#            r = requests.post("https://api.pushover.net/1/messages.json", data = {
#                "token": PUSHOVER_API_TOKEN,
#                "user": PUSHOVER_USER_KEY,
#                "message": '\n'.join(notification),
#                "title": f"COVID Update: {entry['attributes']['NAMELABEL']} county"
#                }
##                files = {
##                    "attachment": ("image.jpg", open("your_image.jpg", "rb"), "image/jpeg")
##                }
#            )

#######################################
# County Statistics
#######################################
if len(counties_monitored) > 0:
    # Output county-level statistics
    for entry in results['features']:
        if entry['attributes']['NAME'] in counties_monitored:
            notification = [
                f"{entry['attributes']['NAMELABEL'] + ' County'}",
                f"New Cases: {entry['attributes']['NewCases']: >15}",
                f"Total Active: {entry['attributes']['TotalActive']: >12}",
                f"Hospitalized: {entry['attributes']['HospitalizationCount']: >12}",
                f"Total Cases: {entry['attributes']['Total']: >13}",
                f"Total Recovered: {entry['attributes']['TotalRecovered']: >9}",
                f"Total Deaths: {entry['attributes']['TotalDeaths']: >12}",
                ]

            if DEBUG:
                print('\n'.join(notification))
                print()
            else:
                # Build a message per county. Stolen from the first todo on Twilio's site.
                for phone_number in phone_numbers:
                    message = client.messages.create(
                        body='\n'.join(notification),
                        messaging_service_sid=TWILIO_MESSAGING_SERVICE,
                        to=phone_number
                        )

#                # Pushover message sender
#                r = requests.post("https://api.pushover.net/1/messages.json", data = {
#                    "token": PUSHOVER_API_TOKEN,
#                    "user": PUSHOVER_USER_KEY,
#                    "message": '\n'.join(notification),
#                    "title": f"COVID Update: {entry['attributes']['NAMELABEL']} county"
#                    }
#                     files = {
#                         "attachment": ("image.jpg", open("your_image.jpg", "rb"), "image/jpeg")
#                     }
#                )
