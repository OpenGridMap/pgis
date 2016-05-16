from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask_environments import Environments
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from app.js_assets import non_admin_js_files, admin_js_files
from app.css_assets import non_admin_css_files, admin_css_files

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

js = Bundle(*non_admin_js_files, filters='jsmin', output='gen/packed.js')
admin_js = Bundle(*admin_js_files, filters='jsmin', output='gen/admin_packed.js')

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

