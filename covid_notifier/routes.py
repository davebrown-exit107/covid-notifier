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
from twilio.twiml.messaging_response import MessagingResponse

###########################################
# import application components
############################################
#from covid_notifier.app import db
from covid_notifier.app import notifier_app
from covid_notifier.helpers import insert_results, send_message_twilio
from covid_notifier.models import Region, Entry, Subscriber
from covid_notifier.sms_handlers import sms_dispatcher 


# Handle incoming SMS messages
@notifier_app.route('/incoming/', methods=['POST'])
def incoming_sms():
    '''Handle incoming SMS messages.'''
    message = dict(request.form)
    body = message['Body']

    command = body.split(' ')[0]
    if command.lower() in sms_dispatcher:
        response = sms_dispatcher[command.lower()](message)
    else:
        response = MessagingResponse()
        response.message("I don't recognize that command. Send 'help' if you need assistance.")

    return str(response)

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
