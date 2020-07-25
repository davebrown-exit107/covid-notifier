# pylint: disable=wrong-import-position
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring

import os

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
# Set some constants
##################################################
notifier_app.config['BASE_URL'] = 'https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/0/query?'
notifier_app.config['RET_FORMAT'] = 'json'
notifier_app.config['WHERE_QUERY'] = 'Total <> 0'
notifier_app.config['RETURN_GEOMETRY'] = 'false'
notifier_app.config['SPATIAL_REL'] = 'esriSpatialRelIntersects'
notifier_app.config['OUT_FIELDS'] = 'orderByFields=NewCases desc,NAMELABEL asc&outSR=102100'
notifier_app.config['RESULT_OFFSET'] = '0'
notifier_app.config['RESULT_RECORD_COUNT'] = '56'
notifier_app.config['RESULT_TYPE'] = 'standard'
notifier_app.config['CACHE_HINT'] = 'true'

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
