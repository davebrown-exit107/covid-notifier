# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=unused-import
# pylint: disable=wrong-import-position

##########################################
# Stdlib imports
###########################################
import os

##########################################
# 3rd party imports
###########################################
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy_utils import database_exists, create_database

# Import blueprint apps
#from .sms.routes import sms_bp

##################################################
# Initialze Application
##################################################
notifier_app = Flask(__name__)

##################################################
# Configure Application
##################################################
envvars = {key:value for (key, value) in os.environ.items() if 'COVID_' in key}
for key, value in envvars.items():
    notifier_app.config[key[6:]] = value

##################################################
# SQLAlchemy setup
##################################################
db = SQLAlchemy(notifier_app)
db.create_all()

##################################################
# flask-migrate setup
##################################################
migrate = Migrate(notifier_app, db)

##################################################
# Register blueprints
##################################################
#notifier_app.register_blueprint(sms_bp)
import covid_notifier.routes
