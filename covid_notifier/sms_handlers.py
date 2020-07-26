'''Handlers for the various SMS command messages'''

##########################################
# 3rd party imports
###########################################
from flask import url_for
from itsdangerous.url_safe import URLSafeTimedSerializer
from twilio.twiml.messaging_response import MessagingResponse

##########################################
# Application component imports
###########################################
from covid_notifier.app import db, notifier_app
from covid_notifier.models import Region, Subscriber
from covid_notifier.helpers import send_message_twilio

def user_help():
    '''Send a help menu.'''
    response = MessagingResponse()
    help_message = '''
# User registration/unregistration
register:  Register your phone number for updates
unregister:  Unregister your phone number for updates

# Helper commands
commands:  Display this message
dashboard:  Send a time sensitive link to the subscriber's dashboard
regions:  List available regions for subscription
subscriptions:  List subscribed regions for this phone number
update:  Request an update on all regions you are subscribed to

# Modify subscriptions
add:  Add a region to your subscriptions
remove:  Remove a region from your subscriptions
Msg&Data Rates May Apply.
'''
    response.message(help_message)
    return response


# User configuration
def register_user(message):
    '''Register a subscriber.'''
    subscriber = Subscriber(phone_number=message['From'])
    db.session.add(subscriber)
    db.session.commit()
    response = MessagingResponse()
    response.message("You are now registered to receive updates. Send 'commands' if you need assistance. Msg&Data Rates May Apply.")
    return response

def unregister_user(message):
    '''Unregister a subscriber.'''
    subscriber = Subscriber.query.filter_by(phone_number=message['From']).one_or_none()
    if subscriber:
        db.session.delete(subscriber)
        db.session.commit()
        response = MessagingResponse()
        response.message('You are no longer registered to receive updates.')
        return response
    return 'Subscriber not found'

def list_regions(message):
    '''Send the subscriber a list of subscribed regions.'''
    response = MessagingResponse()
    message = ['Available regions:']
    message.extend([f'{region.name_label}:  {region.name_abbr}' for region in Region.query.all()])
    response.message('\n'.join(message))
    return response

def list_subscriptions(message):
    '''Send the subscriber a list of subscribed regions.'''
    subscriber = Subscriber.query.filter_by(phone_number=message['From']).one_or_none()
    if subscriber:
        response = MessagingResponse()
        message = ['Your current subscriptions:']
        message.extend([f'{region.name_label}:  {region.name_abbr}' for region in subscriber.regions])
        response.message('\n'.join(message))
        return response
    return 'Subscriber not found'

def user_dashboard(message):
    '''Send the subscriber a link to advanced configuration page.'''
    subscriber = Subscriber.query.filter_by(phone_number=message['From']).one_or_none()
    if subscriber:
        message = ['Your configuration link:']

        serializer = URLSafeTimedSerializer(notifier_app.config['SECRET_KEY'])
        token = serializer.dumps(subscriber.phone_number)
        message.append(url_for('user_dashboard', _external=True, token=token))

        response = MessagingResponse()
        response.message('\n'.join(message))
        return response
    return 'Subscriber not found'

def remove_subscription(message):
    '''Region a region from a subscriber's subscriptions.'''
    subscriber = Subscriber.query.filter_by(phone_number=message['From']).one_or_none()
    region = Region.query.filter_by(name_abbr=message['Body'].split(' ')[1].upper()).one_or_none()
    if subscriber and region and region in subscriber.regions:
        subscriber.regions.remove(region)
        db.session.add(subscriber)
        db.session.commit()

        response = MessagingResponse()
        message = [f'{region.name_label} removed from your subscriptions.']
        response.message('\n'.join(message))
        return response
    return 'Subscriber not found'

def add_subscription(message):
    '''Add a new region to a subscriber's subscriptions.'''
    subscriber = Subscriber.query.filter_by(phone_number=message['From']).one_or_none()
    region = Region.query.filter_by(name_abbr=message['Body'].split(' ')[1].upper()).one_or_none()
    if subscriber and region:
        subscriber.regions.append(region)
        db.session.add(subscriber)
        db.session.commit()

        response = MessagingResponse()
        message = [f'{region.name_label} added to your subscriptions.']
        response.message('\n'.join(message))
        return response
    return 'Subscriber or region not found'

def request_update(message):
    '''Send the subscriber an update for all of their subscribed regions.'''
    subscriber = Subscriber.query.filter_by(phone_number=message['From']).one_or_none()
    if subscriber and len(subscriber.regions) >= 1:
        response = MessagingResponse()
        messages = []
        for region in subscriber.regions:
            today = region.entries[-1]
            yesterday = region.entries[-2]
            if region.name_label == 'Montana':
                message = [f"{region.name_label}"]
            else:
                message = [f"{region.name_label + ' County'}"]
            # There's probably a much better way of handling DIVBYZERO errors but this is what I have right now
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

            response.append(response.message('\n'.join(message)))
        return response
    return 'Subscriber or regions not found'

sms_dispatcher = {
        # User registration/unregistration
        'register': register_user,
        'unregister': unregister_user,
        # Helper commands
        'commands': user_help,
        'dashboard': user_dashboard,
        'regions': list_regions,
        'subscriptions': list_subscriptions,
        'update': request_update,
        # Modify subscriptions
        'add': add_subscription,
        'remove': remove_subscription
        }
