'''Routes for the flask application'''

##########################################
# Stdlib imports
###########################################
from datetime import datetime
from urllib.parse import quote

##########################################
# 3rd party imports
###########################################
from flask import request, render_template, redirect, url_for, flash, abort
from itsdangerous.exc import BadSignature, SignatureExpired
from itsdangerous.url_safe import URLSafeTimedSerializer
import requests
from twilio.twiml.messaging_response import MessagingResponse
from werkzeug.urls import url_parse

from twilio.rest import Client
##########################################
# Application component imports
###########################################
from covid_notifier.app import notifier_app
from covid_notifier.commands import pull_new_data
from covid_notifier.helpers import insert_results, newer_data_available
from covid_notifier.models import Region, Subscriber
from covid_notifier.sms_handlers import sms_dispatcher


@notifier_app.route('/incoming/', methods=['POST'])
def incoming_sms():
    '''Handle incoming SMS messages.'''
    message = dict(request.form)
    body = message['Body']

    # Figure out what command the user wants to run
    command = body.split(' ')[0]

    # Route to the appropriate SMS handler based on the command name
    if command.lower() in sms_dispatcher:
        response = sms_dispatcher[command.lower()](message)
    else:
        response = MessagingResponse()
        response.message("I don't recognize that command. Send 'commands' if you need assistance.")

    return str(response)

@notifier_app.route('/user_dashboard/', methods=['GET'])
@notifier_app.route('/user_dashboard/<token>/', methods=['GET'])
def user_dashboard(token=None):
    '''Show the user their dashboard.'''
    if token:
        serializer = URLSafeTimedSerializer(notifier_app.config['SECRET_KEY'])
        try:
            phone_number = serializer.loads(token, max_age=300)
        except BadSignature:
            return abort(404)
        except SignatureExpired:
            return abort(404)

        subscriber = Subscriber.query.filter_by(phone_number=phone_number).one_or_none()
        if subscriber:
            return render_template('user_dashboard.html.j2', subscriber=subscriber)
# Fun debugging code. This will generate a token on a GET without a token
# Just change PHONENUMBER to one in the database.
#    message = sms_dispatcher['dashboard']({'From': 'PHONENUMBER'})
#    return str(message)
    return abort(404)

@notifier_app.route('/', methods=['GET'])
@notifier_app.route('/state_dashboard/', methods=['GET'])
def state_dashboard():
    '''Display a statewide dashboard.'''
    regions = Region.query.all()
    return render_template('state_dashboard.html.j2', regions=regions)

@notifier_app.route('/region/<region_id>/dashboard/', methods=['GET'])
def region_dashboard(region_id):
    '''Show an individual region's dashboard.'''
    region = Region.query.get(region_id)
    return render_template('region_dashboard.html.j2', region=region)

@notifier_app.route('/pull_updates/')
def web_pull_new_data():
    '''Web trigger to attempt to pull new data.'''

##############################################
# If new data is available, pull all records #
##############################################
    if newer_data_available():
        # Pull new data from the state.
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
        results = requests.get(full_url).json()

        # Find the date on the database
        url = 'https://services.arcgis.com/qnjIrwR8z5Izc0ij/arcgis/rest/services/COVID_Cases_Production_View/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=ScriptRunDate%20desc&resultOffset=0&resultRecordCount=1&resultType=standard&cacheHint=true'
        date_result = requests.get(url).json()
        current = datetime.fromtimestamp(date_result['features'][0]['attributes']['ScriptRunDate'] / 1000).date()

        # Insert the results into the database
        insert_results(results, current)
    return redirect(url_for('state_dashboard'))
