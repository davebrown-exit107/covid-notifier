'''Commands for the flask application'''

##########################################
# Stdlib imports
###########################################
from datetime import datetime
from urllib.parse import quote

##########################################
# 3rd party imports
###########################################
import click
import requests
from twilio.rest import Client

##########################################
# Application component imports
###########################################
from covid_notifier.app import notifier_app
from covid_notifier.helpers import insert_results, newer_data_available
from covid_notifier.models import Subscriber

@notifier_app.cli.command('send-updates')
def update_all_subscribers():
    '''Update all subscribers for all of their subscribed regions.'''
    # Build the Twilio client
    client = Client(notifier_app.config['TWILIO_ACCOUNT_SID'], notifier_app.config['TWILIO_AUTH_TOKEN'])
    subscribers = Subscriber.query.all()
    for subscriber in subscribers:
        if subscriber and len(subscriber.regions) > 0:
            for region in subscriber.regions:
                today = region.entries[-1]
                yesterday = region.entries[-2]
                if region.name_label == 'Montana':
                    message = [f"{region.name_label} - {today.date}"]
                else:
                    message = [f"{region.name_label + ' County'} - {today.date}"]

                # There's probably a much better way of handling
                # DIVBYZERO errors but this is what I have right now
                if today.new_case == 0 or yesterday.new_case == 0:
                    message.append(f"New Cases: {today.new_case: >15} (N/A)")
                else:
                    message.append(f"New Cases: {today.new_case: >15} ({((today.new_case / yesterday.new_case) - 1):+3.0%})")

                if today.total_active == 0 or yesterday.total_active == 0:
                    message.append(f"Total Active: {today.total_active: >12} (N/A)")
                else:
                    message.append(f"Total Active: {today.total_active: >12} ({((today.total_active / yesterday.total_active) - 1):+3.0%})")

                if today.hospitalization_count == 0 or yesterday.hospitalization_count == 0:
                    message.append(f"Hospitalized: {today.hospitalization_count: >12} (N/A)")
                else:
                    message.append(f"Hospitalized: {today.hospitalization_count: >12} ({((today.hospitalization_count / yesterday.hospitalization_count) - 1):+3.0%})")

                if today.total == 0 or yesterday.total == 0:
                    message.append(f"Total Cases: {today.total: >13} (N/A)")
                else:
                    message.append(f"Total Cases: {today.total: >13} ({((today.total / yesterday.total) - 1):+3.0%})")

                if today.total_recovered == 0 or yesterday.total_recovered == 0:
                    message.append(f"Total Recovered: {today.total_recovered: >9} (N/A)")
                else:
                    message.append(f"Total Recovered: {today.total_recovered: >9} ({((today.total_recovered / yesterday.total_recovered) - 1):+3.0%})")

                if today.total_deaths == 0 or yesterday.total_deaths == 0:
                    message.append(f"Total Deaths: {today.total_deaths: >12} (N/A)")
                else:
                    message.append(f"Total Deaths: {today.total_deaths: >12} ({((today.total_deaths / yesterday.total_deaths) - 1):+3.0%})")

                client.messages.create(
                    body='\n'.join(message),
                    messaging_service_sid=notifier_app.config['TWILIO_MESSAGING_SERVICE'],
                    to=subscriber.phone_number
                    )


@notifier_app.cli.command('pull-updates')
def pull_new_data():
    '''Pull new data from the state.'''
    if newer_data_available():
        click.echo('Newer data found online')
        base_url = 'https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/0/query?'
        ret_format = 'json'
        where_query = 'Total <> 0'
        return_geometry = 'false'
        spatial_rel = 'esriSpatialRelIntersects'
        out_fields = 'orderByFields=NewCases desc,NAMELABEL asc&outSR=102100'
        result_offset = '0'
        result_record_count = '56'
        result_type = 'standard'
        cache_hint = 'true'

        click.echo('Building query')
        query_options = [
            "f={}".format(quote(ret_format)),
            "&where={}".format(quote(where_query)),
            "&returnGeometry={}".format(quote(return_geometry)),
            "&spatialRel={}".format(quote(spatial_rel)),
            "&outFields=*&{}".format(quote(out_fields)),
            "&resultOffset={}".format(quote(result_offset)),
            "&resultRecordCount={}".format(quote(result_record_count)),
            "&resultType={}".format(quote(result_type)),
            "&cacheHint={}".format(quote(cache_hint))
            ]

        full_url = ''.join([base_url, ''.join(query_options)])

        # Run the query
        click.echo('Requesting data')
        results = requests.get(full_url).json()

        # Find the date on the database
        url = 'https://services.arcgis.com/qnjIrwR8z5Izc0ij/arcgis/rest/services/COVID_Cases_Production_View/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=ScriptRunDate%20desc&resultOffset=0&resultRecordCount=1&resultType=standard&cacheHint=true'
        date_result = requests.get(url).json()
        current = datetime.fromtimestamp(date_result['features'][0]['attributes']['ScriptRunDate'] / 1000).date()

        # Insert the results into the database
        click.echo('Processing results and committing to the database')
        insert_results(results, current)

        click.echo(f'Results for {current} added to the database.')
        return True
    else:
        click.echo('No newer data found online')
        return False
