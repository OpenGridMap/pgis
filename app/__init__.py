from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask_environments import Environments
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

# for using a current jQuery version from cdn instead of jQuery 1
from flask_bootstrap import WebCDN

import os

# Create app
GisApp = Flask(__name__)
Bootstrap(GisApp)
# for using jQuery 2 from cdn instead of jQuery 1
# (https://github.com/mbr/flask-bootstrap/blob/master/docs/faq.rst#how-can-i-use-jquery2-instead-of-jquery1)
GisApp.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
    '//cdnjs.cloudflare.com/ajax/libs/jquery/2.2.1/'
)
# GisApp.config.from_object('config')
db = SQLAlchemy(GisApp)

env = Environments(GisApp) 
env.from_object('config')

# Assets
assets = Environment(GisApp)
js = Bundle('javascripts/leaflet-src.js', 'javascripts/leaflet.markercluster-src.js','javascripts/handlebars-v3.0.3.js', 'javascripts/Control.Geocoder.js','javascripts/Control.LinkButton.js','javascripts/underscore-min.js','javascripts/L.Control.Sidebar.js', 'javascripts/Control.Loading.js', 'javascripts/main.js',
            filters='jsmin', output='gen/packed.js')

admin_js = Bundle('javascripts/leaflet-src.js', 'javascripts/admin_main.js', 'javascripts/leaflet.draw-src.js','javascripts/handlebars-v3.0.3.js','javascripts/underscore-min.js', 'javascripts/leaflet.markercluster-src.js',
            filters='jsmin', output='gen/admin_packed.js')
assets.register('application_js', js)
assets.register('admin_application_js', admin_js)

less = Bundle('stylesheets/leaflet.css', 'stylesheets/main.less.css', 'stylesheets/MarkerCluster.css', 'stylesheets/MarkerCluster.Default.css','stylesheets/leaflet.draw.css', 'stylesheets/Control.Geocoder.css','stylesheets/L.Control.Sidebar.css', 'stylesheets/Control.Loading.css', 'stylesheets/Control.LinkButton.css',
              filters='less,cssmin', output='gen/packed.css')
admin_less = Bundle('stylesheets/leaflet.css', 'stylesheets/admin_main.less.css','stylesheets/leaflet.draw.css', 'stylesheets/MarkerCluster.css', 'stylesheets/MarkerCluster.Default.css',
              filters='less,cssmin', output='gen/admin_packed.css')

assets.register('application_css', less)
assets.register('admin_application_css', admin_less)

# Load Routes
from app import routes

