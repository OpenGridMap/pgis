from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask_environments import Environments
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import os

# Create app
GisApp = Flask(__name__)
Bootstrap(GisApp)
# GisApp.config.from_object('config')
db = SQLAlchemy(GisApp)

env = Environments(GisApp) 
env.from_object('config')

# Assets
assets = Environment(GisApp)
js = Bundle('javascripts/leaflet-src.js', 'javascripts/leaflet.markercluster-src.js','javascripts/handlebars-v3.0.3.js', 'javascripts/Control.Geocoder.js','javascripts/Control.LinkButton.js','javascripts/underscore-min.js','javascripts/L.Control.Sidebar.js', 'javascripts/Control.Loading.js', 'javascripts/main.js',
            filters='jsmin', output='gen/packed.js')

admin_js = Bundle('javascripts/leaflet-src.js', 'javascripts/jquery-2.1.3.min.js', 'javascripts/admin_main.js', 'javascripts/leaflet.draw-src.js','javascripts/handlebars-v3.0.3.js','javascripts/underscore-min.js', 'javascripts/leaflet.markercluster-src.js',
            filters='jsmin', output='gen/admin_packed.js')
assets.register('application_js', js)
assets.register('admin_application_js', admin_js)

less = Bundle('stylesheets/leaflet.css', 'stylesheets/main.less.css', 'stylesheets/MarkerCluster.css', 'stylesheets/MarkerCluster.Default.css','stylesheets/leaflet.draw.css', 'stylesheets/Control.Geocoder.css','stylesheets/L.Control.Sidebar.css', 'stylesheets/Control.Loading.css', 'stylesheets/Control.LinkButton.css',
              filters='less,cssmin', output='gen/packed.css')
admin_less = Bundle('stylesheets/leaflet.css', 'stylesheets/admin_main.less.css','stylesheets/leaflet.draw.css',
              filters='less,cssmin', output='gen/admin_packed.css')

assets.register('application_css', less)
assets.register('admin_application_css', admin_less)

# Load Routes
from app import routes

