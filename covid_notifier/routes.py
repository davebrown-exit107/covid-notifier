# pylint: disable=no-member
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring

##########################################
# 3rd party modules
###########################################
from datetime import date
from flask import request, render_template, redirect, url_for, flash
import requests
from urllib.parse import quote
from werkzeug.urls import url_parse

###########################################
# import application components
############################################
#from covid_notifier.app import db
from covid_notifier.app import notifier_app
from covid_notifier.helpers import insert_results, send_message_twilio
from covid_notifier.models import Region, Entry, Subscriber


# User registration
@notifier_app.route('/register/<pn>/', methods=['POST'])
def register_user(pn):
    pass

@notifier_app.route('/unregister/<pn>/', methods=['POST'])
def unregister_user(pn):
    pass

@notifier_app.route('/request_update/<pn>/', methods=['GET'])
def request_update(pn):
    subscriber = Subscriber.query.filter_by(phone_number=pn).one_or_none()
    if subscriber and len(subscriber.regions) >= 1:
        for region in subscriber.regions:
            today = region.entries[-1]
            yesterday = region.entries[-2]
            if region.name_label == 'Montana':
                notification = [f"{region.name_label}"]
            else:
                notification = [f"{region.name_label + ' County'}"]
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

            if 'NO_SMS' in notifier_app.config:
                print('\n'.join(notification))
            else:
                send_message_twilio(notification, subscriber.phone_number)
    return 'message sent'

# User configuration
@notifier_app.route('/config/<pn>/', methods=['POST'])
def user_config(pn):
    pass

# Inbound SMS

# Outbound SMS

# Admin
@notifier_app.route('/user_dashboard/<pn>/', methods=['GET'])
def user_dashboard(pn):
    subscriber = Subscriber.query.filter_by(phone_number=pn).one_or_none()
    if subscriber:
        return render_template('user_dashboard.html.j2', subscriber=subscriber)

@notifier_app.route('/state_dashboard/', methods=['GET'])
def state_dashboard():
    regions = Region.query.all()
    return render_template('state_dashboard.html.j2', regions=regions)

@notifier_app.route('/region/<region_id>/dashboard/', methods=['GET'])
def region_dashboard(region_id):
    region = Region.query.get(region_id)
    return render_template('region_dashboard.html.j2', region=region)

@notifier_app.route('/pull_new_data/')
def pull_new_data():
    # Fill in the params from the above constants
    query_options = [
        "f={}".format(quote(notifier_app.config['RET_FORMAT'])),
        "&where={}".format(quote(notifier_app.config['WHERE_QUERY'])),
        "&returnGeometry={}".format(quote(notifier_app.config['RETURN_GEOMETRY'])),
        "&spatialRel={}".format(quote(notifier_app.config['SPATIAL_REL'])),
        "&outFields=*&{}".format(quote(notifier_app.config['OUT_FIELDS'])),
        "&resultOffset={}".format(quote(notifier_app.config['RESULT_OFFSET'])),
        "&resultRecordCount={}".format(quote(notifier_app.config['RESULT_RECORD_COUNT'])),
        "&resultType={}".format(quote(notifier_app.config['RESULT_TYPE'])),
        "&cacheHint={}".format(quote(notifier_app.config['CACHE_HINT']))
        ]

    full_url = ''.join([notifier_app.config['BASE_URL'], ''.join(query_options)])

    # Run the query
    results = requests.get(full_url).json()

    # Insert the results into the database
    insert_results(results, date.today())

    # Redirect to the statewide dashboard
    return redirect(state_dashboard)
