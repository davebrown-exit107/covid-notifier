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
from covid_notifier.models import Region, Entry


# User registration
@notifier_app.route('/register/<pn>/', methods=['POST'])
def register_user(pn):
    pass

@notifier_app.route('/unregister/<pn>/', methods=['POST'])
def unregister_user(pn):
    pass

@notifier_app.route('/update/<pn>/', methods=['POST'])
def send_update(pn):
    pass

# User configuration
@notifier_app.route('/config/<pn>/', methods=['POST'])
def user_config(pn):
    pass

# Inbound SMS

# Outbound SMS

# Admin
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
