import osmapi
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_bootstrap import WebCDN
from flask_environments import Environments

from app.css_assets import non_admin_css_files, admin_css_files, gallery_css_files
from app.js_assets import non_admin_js_files, admin_js_files, gallery_js_files

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
gallery_js = Bundle(*gallery_js_files, filters='jsmin', output='gen/gallery_packed.js')

assets.register('application_js', js)
assets.register('admin_application_js', admin_js)
assets.register('gallery_application_js', gallery_js)

less = Bundle('stylesheets/leaflet.css', 'stylesheets/main.css', 'stylesheets/MarkerCluster.css',
              'stylesheets/MarkerCluster.Default.css', 'stylesheets/leaflet.draw.css',
              'stylesheets/Control.Geocoder.css', 'stylesheets/L.Control.Sidebar.css',
              'stylesheets/Control.Loading.css', 'stylesheets/Control.LinkButton.css',
              'stylesheets/font-awesome.min.css',
              filters='less,cssmin', output='gen/packed.css')
admin_less = Bundle('stylesheets/leaflet.css', 'stylesheets/admin_main.less.css', 'stylesheets/leaflet.draw.css',
                    'stylesheets/MarkerCluster.css', 'stylesheets/MarkerCluster.Default.css',
                    filters='less,cssmin', output='gen/admin_packed.css')
gallery_less = Bundle(*gallery_css_files, filters='less,cssmin', output='gen/gallery_packed.css')

assets.register('application_css', less)
assets.register('admin_application_css', admin_less)
assets.register('gallery_application_css', gallery_less)

# Load Routes
from app import routes

# Load Jinja2 template filters
from app.helpers import template_filters

# configure OSM Api
GisApp.osmApiClient = osmapi.OsmApi(
    api=GisApp.config['OSMAPI_CONFIG']['domain'],
    username=GisApp.config['OSMAPI_CONFIG']['username'],
    password=GisApp.config['OSMAPI_CONFIG']['password']
)
