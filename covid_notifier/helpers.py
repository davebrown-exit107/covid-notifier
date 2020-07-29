# pylint: disable=line-too-long
# pylint: disable=too-many-statements
'''Help poor developers from having to repeat themselves...'''

##########################################
# Stdlib imports
###########################################
from datetime import datetime

##########################################
# 3rd parth imports
###########################################
import requests
from twilio.rest import Client

##########################################
# Application component imports
###########################################
from covid_notifier.models import Region, Entry
from covid_notifier.app import db, notifier_app

def send_message_twilio(message, phone_number):
    '''Send a notification via twilio.'''
    # Build the Twilio client
    client = Client(
        notifier_app.config['TWILIO_ACCOUNT_SID'],
        notifier_app.config['TWILIO_AUTH_TOKEN'])

    # Build a message per county. Stolen from the first todo on Twilio's site.
    message = client.messages.create(
        body='\n'.join(message),
        messaging_service_sid=notifier_app.config['TWILIO_MESSAGING_SERVICE'],
        to=phone_number
        )

    return message

def newer_data_available():
    '''Checks to see if the data has been updated on the source site.'''
    url = 'https://services.arcgis.com/qnjIrwR8z5Izc0ij/arcgis/rest/services/COVID_Cases_Production_View/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=ScriptRunDate%20desc&resultOffset=0&resultRecordCount=1&resultType=standard&cacheHint=true'
    results = requests.get(url).json()
    current = datetime.fromtimestamp(results['features'][0]['attributes']['ScriptRunDate'] / 1000).date()
    database = Entry.query.all()[-1].date
    return current > database

def insert_results(results, update_date):
    '''Process the json return from a query to the ArcGIS database.'''

    #######################################
    # Statewide Statistics
    #######################################
    # Store statewide statistics

    # Make sure that the statewide region exists
    state = db.session.query(Region).filter_by(name='MONTANA').one_or_none()
    if not state:
        state = Region(
            name='MONTANA',
            name_label='Montana',
            name_abbr='MT',
            county_number='9999',
            fips='None')

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
