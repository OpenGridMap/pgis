import osmapi
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_environments import Environments

# Create app
GisGeneratorApp = Flask(__name__)
Bootstrap(GisGeneratorApp)

# GisApp.config.from_object('config')
db = SQLAlchemy(GisGeneratorApp)

env = Environments(GisGeneratorApp)
env.from_object('config')

# Load Routes
from app import routes

# configure OSM Api
GisGeneratorApp.osmApiClient = osmapi.OsmApi(
    api=GisGeneratorApp.config['OSMAPI_CONFIG']['domain'],
    username=GisGeneratorApp.config['OSMAPI_CONFIG']['username'],
    password=GisGeneratorApp.config['OSMAPI_CONFIG']['password']
)
