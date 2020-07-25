#!/usr/bin/env python
'''Help poor developers from having to repeat themselves...'''

from twilio.rest import Client
import requests

from covid_notifier.models import Region, Entry
from covid_notifier.app import db, notifier_app

def send_message_twilio(message, phone_number):
    '''Send a notification via twilio.'''

    # Build the Twilio client
    client = Client(notifier_app.config['TWILIO_ACCOUNT_SID'], notifier_app.config['TWILIO_AUTH_TOKEN'])
    #max_title_len = max(entry[0] in stats)
    #print(max_title_len)
    #message = [f"{title}: {stat}" for (title,stat) in stats]

    # Build a message per county. Stolen from the first todo on Twilio's site.
    message = client.messages.create(
        body='\n'.join(message),
        messaging_service_sid=notifier_app.config['TWILIO_MESSAGING_SERVICE'],
        to=phone_number
        )

    return message


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


def insert_results(results, update_date):
    '''Process the json return from a query to the ArcGIS database.'''

    #######################################
    # Statewide Statistics
    #######################################
    # Store statewide statistics

    # Make sure that the statewide region exists
    state = db.session.query(Region).filter_by(name='MONTANA').one_or_none()
    if not state:
        state = Region(name='MONTANA', name_label='Montana', name_abbr='MT', county_number='9999', fips='None') 

    state_entry = Entry(region=state, date=update_date)

    state_entry.f_0_9 = sum(entry['attributes']['F_0_9'] for entry in results['features'])
    state_entry.m_0_9 = sum(entry['attributes']['M_0_9'] for entry in results['features'])
    state_entry.t_0_9 = sum(entry['attributes']['T_0_9'] for entry in results['features'])
    state_entry.f_10_19 = sum(entry['attributes']['F_10_19'] for entry in results['features'])
    state_entry.m_10_19 = sum(entry['attributes']['M_10_19'] for entry in results['features'])
    state_entry.t_10_19 = sum(entry['attributes']['T_10_19'] for entry in results['features'])
    state_entry.f_20_29 = sum(entry['attributes']['F_20_29'] for entry in results['features'])
    state_entry.m_20_29 = sum(entry['attributes']['M_20_29'] for entry in results['features'])
    state_entry.t_20_29 = sum(entry['attributes']['T_20_29'] for entry in results['features'])
    state_entry.f_30_39 = sum(entry['attributes']['F_30_39'] for entry in results['features'])
    state_entry.m_30_39 = sum(entry['attributes']['M_30_39'] for entry in results['features'])
    state_entry.t_30_39 = sum(entry['attributes']['T_30_39'] for entry in results['features'])
    state_entry.f_40_49 = sum(entry['attributes']['F_40_49'] for entry in results['features'])
    state_entry.m_40_49 = sum(entry['attributes']['M_40_49'] for entry in results['features'])
    state_entry.t_40_49 = sum(entry['attributes']['T_40_49'] for entry in results['features'])
    state_entry.f_50_59 = sum(entry['attributes']['F_50_59'] for entry in results['features'])
    state_entry.m_50_59 = sum(entry['attributes']['M_50_59'] for entry in results['features'])
    state_entry.t_50_59 = sum(entry['attributes']['T_50_59'] for entry in results['features'])
    state_entry.f_60_69 = sum(entry['attributes']['F_60_69'] for entry in results['features'])
    state_entry.m_60_69 = sum(entry['attributes']['M_60_69'] for entry in results['features'])
    state_entry.t_60_69 = sum(entry['attributes']['T_60_69'] for entry in results['features'])
    state_entry.f_70_79 = sum(entry['attributes']['F_70_79'] for entry in results['features'])
    state_entry.m_70_79 = sum(entry['attributes']['M_70_79'] for entry in results['features'])
    state_entry.t_70_79 = sum(entry['attributes']['T_70_79'] for entry in results['features'])
    state_entry.f_80_89 = sum(entry['attributes']['F_80_89'] for entry in results['features'])
    state_entry.m_80_89 = sum(entry['attributes']['M_80_89'] for entry in results['features'])
    state_entry.t_80_89 = sum(entry['attributes']['T_80_89'] for entry in results['features'])
    state_entry.f_90_99 = sum(entry['attributes']['F_90_99'] for entry in results['features'])
    state_entry.m_90_99 = sum(entry['attributes']['M_90_99'] for entry in results['features'])
    state_entry.t_90_99 = sum(entry['attributes']['T_90_99'] for entry in results['features'])
    state_entry.f_100 = sum(entry['attributes']['F_100'] for entry in results['features'])
    state_entry.m_100 = sum(entry['attributes']['M_100'] for entry in results['features'])
    state_entry.t_100 = sum(entry['attributes']['T_100'] for entry in results['features'])
    state_entry.new_case = sum(entry['attributes']['NewCases'] for entry in results['features'])
    state_entry.total_deaths = sum(entry['attributes']['TotalDeaths'] for entry in results['features'])
    state_entry.hospitalization_count = sum(entry['attributes']['HospitalizationCount'] for entry in results['features'])
    state_entry.total_recovered = sum(entry['attributes']['TotalRecovered'] for entry in results['features'])
    state_entry.total_active = sum(entry['attributes']['TotalActive'] for entry in results['features'])
    state_entry.total = sum(entry['attributes']['Total'] for entry in results['features'])

    db.session.add(state_entry)
    db.session.commit()
    

    #######################################
    # County Statistics
    #######################################
    # Store county-level statistics
    for entry in results['features']:
        region = db.session.query(Region).filter_by(name=entry['attributes']['NAME']).one_or_none()
        if not region:
            region = Region(
                name=entry['attributes']['NAME'],
                name_label=entry['attributes']['NAMELABEL'],
                name_abbr=entry['attributes']['NAMEABBR'],
                county_number=entry['attributes']['COUNTYNUMBER'],
                fips=entry['attributes']['FIPS']
            )
        # Create the new entry
        db_entry = Entry(region=region, date=update_date)

        # Fill in the details of the entry
        db_entry.f_0_9 = entry['attributes']['F_0_9']
        db_entry.m_0_9 = entry['attributes']['M_0_9']
        db_entry.t_0_9 = entry['attributes']['T_0_9']
        db_entry.f_10_19 = entry['attributes']['F_10_19']
        db_entry.m_10_19 = entry['attributes']['M_10_19']
        db_entry.t_10_19 = entry['attributes']['T_10_19']
        db_entry.f_20_29 = entry['attributes']['F_20_29']
        db_entry.m_20_29 = entry['attributes']['M_20_29']
        db_entry.t_20_29 = entry['attributes']['T_20_29']
        db_entry.f_30_39 = entry['attributes']['F_30_39']
        db_entry.m_30_39 = entry['attributes']['M_30_39']
        db_entry.t_30_39 = entry['attributes']['T_30_39']
        db_entry.f_40_49 = entry['attributes']['F_40_49']
        db_entry.m_40_49 = entry['attributes']['M_40_49']
        db_entry.t_40_49 = entry['attributes']['T_40_49']
        db_entry.f_50_59 = entry['attributes']['F_50_59']
        db_entry.m_50_59 = entry['attributes']['M_50_59']
        db_entry.t_50_59 = entry['attributes']['T_50_59']
        db_entry.f_60_69 = entry['attributes']['F_60_69']
        db_entry.m_60_69 = entry['attributes']['M_60_69']
        db_entry.t_60_69 = entry['attributes']['T_60_69']
        db_entry.f_70_79 = entry['attributes']['F_70_79']
        db_entry.m_70_79 = entry['attributes']['M_70_79']
        db_entry.t_70_79 = entry['attributes']['T_70_79']
        db_entry.f_80_89 = entry['attributes']['F_80_89']
        db_entry.m_80_89 = entry['attributes']['M_80_89']
        db_entry.t_80_89 = entry['attributes']['T_80_89']
        db_entry.f_90_99 = entry['attributes']['F_90_99']
        db_entry.m_90_99 = entry['attributes']['M_90_99']
        db_entry.t_90_99 = entry['attributes']['T_90_99']
        db_entry.f_100 = entry['attributes']['F_100']
        db_entry.m_100 = entry['attributes']['M_100']
        db_entry.t_100 = entry['attributes']['T_100']
        db_entry.notes = entry['attributes']['Notes']
        db_entry.new_case = entry['attributes']['NewCases']
        db_entry.total_deaths = entry['attributes']['TotalDeaths']
        db_entry.hospitalization_count = entry['attributes']['HospitalizationCount']
        db_entry.total_recovered = entry['attributes']['TotalRecovered']
        db_entry.total_active = entry['attributes']['TotalActive']
        db_entry.total = entry['attributes']['Total']

        # Add it to the session and commit
        db.session.add(db_entry)
        db.session.commit()































































































#if __name__ == '__main__':
#    # Send today's notifications.
#    from config import auth, DEBUG
#    from db import engine
#    from db import Region
#    from sqlalchemy.orm import sessionmaker
#
#    # Build our connection to the database
#    Session = sessionmaker(bind=engine)
#    session = Session()
#
#    # Import other vars
#    from sensitive import phone_numbers, counties_monitored, statewide
#
#    if statewide:
#        state = session.query(Region).filter_by(name='MONTANA').one_or_none()
#        today = state.entries[-1]
#        yesterday = state.entries[-2]
#        notification = [f"{state.name_label}"]
#        # There's probably a much better way of handling DIVBYZERO errors but this is what I have right now
#        if today.new_case == 0 or yesterday.new_case == 0:
#            notification.append(f"New Cases: {today.new_case: >15} (N/A)")
#        else:
#            notification.append(f"New Cases: {today.new_case: >15} ({((today.new_case / yesterday.new_case) - 1):+3.0%})")
#
#        if today.total_active == 0 or yesterday.total_active == 0:
#            notification.append(f"Total Active: {today.total_active: >12} (N/A)")
#        else:
#            notification.append(f"Total Active: {today.total_active: >12} ({((today.total_active / yesterday.total_active) - 1):+3.0%})")
#
#        if today.hospitalization_count == 0 or yesterday.hospitalization_count == 0:
#            notification.append(f"Hospitalized: {today.hospitalization_count: >12} (N/A)")
#        else:
#            notification.append(f"Hospitalized: {today.hospitalization_count: >12} ({((today.hospitalization_count / yesterday.hospitalization_count) - 1):+3.0%})")
#
#        if today.total == 0 or yesterday.total == 0:
#            notification.append(f"Total Cases: {today.total: >13} (N/A)")
#        else:
#            notification.append(f"Total Cases: {today.total: >13} ({((today.total / yesterday.total) - 1):+3.0%})")
#
#        if today.total_recovered == 0 or yesterday.total_recovered == 0:
#            notification.append(f"Total Recovered: {today.total_recovered: >9} (N/A)")
#        else:
#            notification.append(f"Total Recovered: {today.total_recovered: >9} ({((today.total_recovered / yesterday.total_recovered) - 1):+3.0%})")
#
#        if today.total_deaths == 0 or yesterday.total_deaths == 0:
#            notification.append(f"Total Deaths: {today.total_deaths: >12} (N/A)")
#        else:
#            notification.append(f"Total Deaths: {today.total_deaths: >12} ({((today.total_deaths / yesterday.total_deaths) - 1):+3.0%})")
#
#        if DEBUG:
#            print('\n'.join(notification))
#        else:
#            send_message_twilio(notification, phone_numbers, auth)
#
#    for county in counties_monitored:
#        county = session.query(Region).filter_by(name=county).one_or_none()
#        today = county.entries[-1]
#        yesterday = county.entries[-2]
#        notification = [f"{county.name_label + ' County'}"]
#        # There's probably a much better way of handling DIVBYZERO errors but this is what I have right now
#        if today.new_case == 0 or yesterday.new_case == 0:
#            notification.append(f"New Cases: {today.new_case: >15} (N/A)")
#        else:
#            notification.append(f"New Cases: {today.new_case: >15} ({((today.new_case / yesterday.new_case) - 1):+3.0%})")
#
#        if today.total_active == 0 or yesterday.total_active == 0:
#            notification.append(f"Total Active: {today.total_active: >12} (N/A)")
#        else:
#            notification.append(f"Total Active: {today.total_active: >12} ({((today.total_active / yesterday.total_active) - 1):+3.0%})")
#
#        if today.hospitalization_count == 0 or yesterday.hospitalization_count == 0:
#            notification.append(f"Hospitalized: {today.hospitalization_count: >12} (N/A)")
#        else:
#            notification.append(f"Hospitalized: {today.hospitalization_count: >12} ({((today.hospitalization_count / yesterday.hospitalization_count) - 1):+3.0%})")
#
#        if today.total == 0 or yesterday.total == 0:
#            notification.append(f"Total Cases: {today.total: >13} (N/A)")
#        else:
#            notification.append(f"Total Cases: {today.total: >13} ({((today.total / yesterday.total) - 1):+3.0%})")
#
#        if today.total_recovered == 0 or yesterday.total_recovered == 0:
#            notification.append(f"Total Recovered: {today.total_recovered: >9} (N/A)")
#        else:
#            notification.append(f"Total Recovered: {today.total_recovered: >9} ({((today.total_recovered / yesterday.total_recovered) - 1):+3.0%})")
#
#        if today.total_deaths == 0 or yesterday.total_deaths == 0:
#            notification.append(f"Total Deaths: {today.total_deaths: >12} (N/A)")
#        else:
#            notification.append(f"Total Deaths: {today.total_deaths: >12} ({((today.total_deaths / yesterday.total_deaths) - 1):+3.0%})")
#
#        if DEBUG:
#            print('\n'.join(notification))
#        else:
#            send_message_twilio(notification, phone_numbers, auth)
