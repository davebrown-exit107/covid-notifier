#!/usr/bin/env python
'''Send notifications by whatever means necessary.'''

from twilio.rest import Client
import requests

def send_message_twilio(message, phone_numbers, auth):
    '''Send a notification via twilio.'''

    # Build the Twilio client
    client = Client(auth['TWILIO_ACCOUNT_SID'], auth['TWILIO_AUTH_TOKEN'])
    #max_title_len = max(entry[0] in stats)
    #print(max_title_len)
    #message = [f"{title}: {stat}" for (title,stat) in stats]

    # Build a message per county. Stolen from the first todo on Twilio's site.
    for phone_number in phone_numbers:
        client.messages.create(
            body='\n'.join(message),
            messaging_service_sid=auth['TWILIO_MESSAGING_SERVICE'],
            to=phone_number
            )


def send_message_pushover(stats, title, auth):
    '''Send a message via Pushover.io'''
    message = [f"{title}: {stat}" for (title,stat) in stats]

    # Pushover message sender
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": auth['PUSHOVER_API_TOKEN'],
        "user": auth['PUSHOVER_USER_KEY'],
        "message": '\n'.join(message),
        "title": f"COVID Update: {title} county"
        })

if __name__ == '__main__':
    # Send today's notifications.
    from config import auth, DEBUG
    from db import engine
    from db import Region
    from sqlalchemy.orm import sessionmaker

    # Build our connection to the database
    Session = sessionmaker(bind=engine)
    session = Session()

    # Import other vars
    from sensitive import phone_numbers, counties_monitored, statewide

    if statewide:
        state = session.query(Region).filter_by(name='MONTANA').one_or_none()
        today = state.entries[-1]
        yesterday = state.entries[-2]
        notification = [f"{state.name_label}"]
        # There's probably a much better way of handling DIVBYZERO errors but this is what I have right now
        if today.new_case == 0 or yesterday.new_case == 0:
            notification.append(f"New Cases: {today.new_case: >15} (N/A)")
        else:
            notification.append(f"New Cases: {today.new_case: >15} ({((today.new_case / yesterday.new_case) - 1):+3.0%})")

        if today.total_active == 0 or yesterday.total_active == 0:
            notification.append(f"Total Active: {today.total_active: >12} (N/A)")
        else:
            notification.append(f"Total Active: {today.total_active: >12} ({((today.total_active / yesterday.total_active) - 1):+3.0%})")

        if today.hospitalization_count == 0 or yesterday.hospitalization_count == 0:
            notification.append(f"Hospitalized: {today.hospitalization_count: >12} (N/A)")
        else:
            notification.append(f"Hospitalized: {today.hospitalization_count: >12} ({((today.hospitalization_count / yesterday.hospitalization_count) - 1):+3.0%})")

        if today.total == 0 or yesterday.total == 0:
            notification.append(f"Total Cases: {today.total: >13} (N/A)")
        else:
            notification.append(f"Total Cases: {today.total: >13} ({((today.total / yesterday.total) - 1):+3.0%})")

        if today.total_recovered == 0 or yesterday.total_recovered == 0:
            notification.append(f"Total Recovered: {today.total_recovered: >9} (N/A)")
        else:
            notification.append(f"Total Recovered: {today.total_recovered: >9} ({((today.total_recovered / yesterday.total_recovered) - 1):+3.0%})")

        if today.total_deaths == 0 or yesterday.total_deaths == 0:
            notification.append(f"Total Deaths: {today.total_deaths: >12} (N/A)")
        else:
            notification.append(f"Total Deaths: {today.total_deaths: >12} ({((today.total_deaths / yesterday.total_deaths) - 1):+3.0%})")

        if DEBUG:
            print('\n'.join(notification))
        else:
            send_message_twilio(notification, phone_numbers, auth)

    for county in counties_monitored:
        county = session.query(Region).filter_by(name=county).one_or_none()
        today = county.entries[-1]
        yesterday = county.entries[-2]
        notification = [f"{county.name_label + ' County'}"]
        # There's probably a much better way of handling DIVBYZERO errors but this is what I have right now
        if today.new_case == 0 or yesterday.new_case == 0:
            notification.append(f"New Cases: {today.new_case: >15} (N/A)")
        else:
            notification.append(f"New Cases: {today.new_case: >15} ({((today.new_case / yesterday.new_case) - 1):+3.0%})")

        if today.total_active == 0 or yesterday.total_active == 0:
            notification.append(f"Total Active: {today.total_active: >12} (N/A)")
        else:
            notification.append(f"Total Active: {today.total_active: >12} ({((today.total_active / yesterday.total_active) - 1):+3.0%})")

        if today.hospitalization_count == 0 or yesterday.hospitalization_count == 0:
            notification.append(f"Hospitalized: {today.hospitalization_count: >12} (N/A)")
        else:
            notification.append(f"Hospitalized: {today.hospitalization_count: >12} ({((today.hospitalization_count / yesterday.hospitalization_count) - 1):+3.0%})")

        if today.total == 0 or yesterday.total == 0:
            notification.append(f"Total Cases: {today.total: >13} (N/A)")
        else:
            notification.append(f"Total Cases: {today.total: >13} ({((today.total / yesterday.total) - 1):+3.0%})")

        if today.total_recovered == 0 or yesterday.total_recovered == 0:
            notification.append(f"Total Recovered: {today.total_recovered: >9} (N/A)")
        else:
            notification.append(f"Total Recovered: {today.total_recovered: >9} ({((today.total_recovered / yesterday.total_recovered) - 1):+3.0%})")

        if today.total_deaths == 0 or yesterday.total_deaths == 0:
            notification.append(f"Total Deaths: {today.total_deaths: >12} (N/A)")
        else:
            notification.append(f"Total Deaths: {today.total_deaths: >12} ({((today.total_deaths / yesterday.total_deaths) - 1):+3.0%})")

        if DEBUG:
            print('\n'.join(notification))
        else:
            send_message_twilio(notification, phone_numbers, auth)
