from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, jsonify, Response
from flask.ext.login import LoginManager, login_user, login_required
from flask_oauthlib.client import OAuth

from app import GisApp, db
import app.models.point
import app.models.powerline
import app.models.user
import app.controllers.application_controller
import app.controllers.points_controller
import app.controllers.powerlines_controller
import app.controllers.admin.application_controller
import app.controllers.admin.points_controller
import app.controllers.admin.powerlines_controller
import app.controllers.admin.users_controller

login_manager = LoginManager()
login_manager.init_app(GisApp)

oauth = OAuth(GisApp)

google = oauth.remote_app(
    'google',
    consumer_key=GisApp.config.get('GOOGLE_CLIENT_ID'),
    consumer_secret=GisApp.config.get('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'

    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@login_manager.user_loader
def load_user(userid):
    return app.models.user.User()

@GisApp.route('/')
@GisApp.route('/index')
def index():
	controller = app.controllers.application_controller.ApplicationController()
	return controller.index()

@GisApp.route('/points')
def points():
	controller = app.controllers.points_controller.PointsController()
	return controller.index()

@GisApp.route('/powerlines', methods=['GET'])
def powerlines():
	controller = app.controllers.powerlines_controller.PowerlinesController()
	return controller.index()	

@GisApp.route('/admin/login')
def admin_login():
    controller = app.controllers.admin.application_controller.ApplicationController()
    return google.authorize(callback=url_for('authorized', _external=True))

@GisApp.route('/admin/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    return jsonify({"data": me.data})

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@GisApp.route('/admin')
@login_required
def admin():
	controller = app.controllers.admin.application_controller.ApplicationController()
	return controller.index()

@GisApp.route('/admin/points')
def admin_points():
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.index()

@GisApp.route('/admin/points/new')
def admin_points_add():	
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.new()

@GisApp.route('/admin/points/create', methods=['POST'])
def admin_points_create():
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.create()

@GisApp.route('/admin/points/delete/<id>', methods=['GET'])
def admin_points_delete(id):
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.delete(id)

@GisApp.route('/admin/powerlines')
def admin_powerlines():
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.index()

@GisApp.route('/admin/powerlines/new')
def admin_powerlines_new():
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.new()

@GisApp.route('/admin/powerlines/create', methods=['POST'])
def admin_powerlines_create():
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.create()

@GisApp.route('/admin/powerlines/edit/<id>', methods=['GET'])
def admin_powerlines_edit(id):
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.edit(id)

@GisApp.route('/admin/powerlines/update/<id>', methods=['POST'])
def admin_powerlines_update(id):
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.update(id)

@GisApp.route('/admin/powerlines/delete/<id>', methods=['GET'])
def admin_powerlines_delete(id):
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.delete(id)

@GisApp.route('/admin/users')
def admin_users():
    controller = app.controllers.admin.users_controller.UsersController()
    return controller.index()

@GisApp.route('/admin/users/new')
def admin_users_new():
    controller = app.controllers.admin.users_controller.UsersController()
    return controller.new()
