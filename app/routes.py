from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, jsonify, Response, current_app
from flask.ext.login import LoginManager, login_user, login_required, logout_user, current_user
from flask_oauthlib.client import OAuth
from flask.ext.principal import Principal, Permission, ActionNeed, identity_loaded, UserNeed, identity_changed, Identity, AnonymousIdentity


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
import app.permissions

login_manager = LoginManager()
login_manager.init_app(GisApp)
login_manager.login_view = "/admin/login"

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



@identity_loaded.connect_via(GisApp)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'action_permissions'):
       for action_permission in current_user.action_permissions:
            identity.provides.add(ActionNeed(action_permission))


@login_manager.user_loader
def load_user(userid):
    return app.models.user.User.query.get(userid)

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
    return controller.login()

@GisApp.route('/admin/do_login')
def admin_do_login():
    return google.authorize(callback=url_for('authorized', _external=True))

@GisApp.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect("/admin/login")

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
    user = app.models.user.User.query.filter_by(email=me.data['email']).first()

    if user is None:
        return 'Your user is not part of a system'
    else:
        login_user(user)        
        # Tell Flask-Principal the identity changed
        identity_changed.send(current_app._get_current_object(),
              identity=Identity(user.id))
        return redirect('/admin')

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
@login_required
@app.permissions.admin_points.require()
def admin_points():
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.index()

@GisApp.route('/admin/points/new')
@login_required
@app.permissions.admin_points_new.require()
def admin_points_new():	
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.new()

@GisApp.route('/admin/points/create', methods=['POST'])
@login_required
@app.permissions.admin_points_create.require()
def admin_points_create():
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.create()

@GisApp.route('/admin/points/edit/<id>')
@login_required
@app.permissions.admin_points_edit.require()
def admin_points_edit(id):
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.edit(id)

@GisApp.route('/admin/points/update/<id>', methods=['POST'])
@login_required
@app.permissions.admin_points_update.require()
def admin_points_update(id):
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.update(id)

@GisApp.route('/admin/points/delete/<id>')
@login_required
@app.permissions.admin_points_delete.require()
def admin_points_delete(id):
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.delete(id)

@GisApp.route('/admin/powerlines')
@login_required
@app.permissions.admin_powerlines.require()
def admin_powerlines():
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.index()

@GisApp.route('/admin/powerlines/new')
@login_required
@app.permissions.admin_powerlines_new.require()
def admin_powerlines_new():
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.new()

@GisApp.route('/admin/powerlines/create', methods=['POST'])
@login_required
@app.permissions.admin_powerlines_create.require()
def admin_powerlines_create():
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.create()

@GisApp.route('/admin/powerlines/edit/<id>', methods=['GET'])
@login_required
@app.permissions.admin_powerlines_edit.require()
def admin_powerlines_edit(id):
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.edit(id)

@GisApp.route('/admin/powerlines/update/<id>', methods=['POST'])
@login_required
@app.permissions.admin_powerlines_update.require()
def admin_powerlines_update(id):
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.update(id)

@GisApp.route('/admin/powerlines/delete/<id>', methods=['GET'])
@login_required
@app.permissions.admin_powerlines_delete.require()
def admin_powerlines_delete(id):
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.delete(id)

@GisApp.route('/admin/users')
@login_required
def admin_users():
    controller = app.controllers.admin.users_controller.UsersController()
    return controller.index()

@GisApp.route('/admin/users/new')
@login_required
def admin_users_new():
    controller = app.controllers.admin.users_controller.UsersController()
    return controller.new()

@GisApp.route('/admin/users/create', methods=['POST'])
@login_required
def admin_users_create():
    controller = app.controllers.admin.users_controller.UsersController()
    return controller.create()

@GisApp.route('/admin/users/delete/<id>')
@login_required
def admin_users_delete(id):
    controller = app.controllers.admin.users_controller.UsersController()
    return controller.delete(id)
