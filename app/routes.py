from flask import redirect, session, url_for, request, json, jsonify, current_app
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.principal import ActionNeed, identity_loaded, UserNeed, identity_changed, \
    Identity
from flask_oauthlib.client import OAuth
from httplib2 import Http

import app.controllers.admin.application_controller
import app.controllers.admin.points_controller
import app.controllers.admin.powerlines_controller
import app.controllers.admin.submissions_controller
import app.controllers.admin.users_controller
import app.controllers.application_controller
import app.controllers.bonus_system_controller
import app.controllers.gallery_controller
import app.controllers.points_controller
import app.controllers.powerlines_controller
import app.controllers.ranking_controller
import app.controllers.relations_controller
import app.controllers.submissions_controller
import app.controllers.transnet_controller
import app.controllers.userprofile_controller
import app.models.point
import app.models.powerline
import app.models.user
import app.permissions
from app import GisApp
from app.controllers.admin.transnset_logs_controller import TransnetLogsController
from app.controllers.admin.transnset_users_controller import TransnetUsersController
from app.controllers.contribution_controller import ContributionController

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


@GisApp.route('/userprofile')
@login_required
def userprofile():
    controller = app.controllers.userprofile_controller.UserprofileController()
    response = controller.index()
    return controller.index()


@GisApp.route('/ranking')
def ranking():
    controller = app.controllers.ranking_controller.RankingController()
    response = controller.index()
    return controller.index()


@GisApp.route('/bonus_system')
def activity_points():
    controller = app.controllers.bonus_system_controller.BonusSystemController()
    response = controller.index()
    return controller.index()


@GisApp.route('/submissions')
def aubmissions():
    controller = app.controllers.submissions_controller.SubmissionsController()
    response = controller.index()
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@GisApp.route('/points')
def points():
    controller = app.controllers.points_controller.PointsController()
    return controller.index()


@GisApp.route('/points/with_properties')
def points_with_properties():
    controller = app.controllers.points_controller.PointsController()
    return controller.with_properties()


@GisApp.route('/points/clustered')
def points_clustered():
    controller = app.controllers.points_controller.PointsController()
    return controller.clustered()


@GisApp.route('/points/edit/<id>')
@login_required
@app.permissions.admin_points_edit.require(http_exception=403)
def points_edit(id):
    controller = app.controllers.points_controller.PointsController()
    return controller.edit(id)


@GisApp.route('/points/update/<id>', methods=['POST'])
@login_required
@app.permissions.admin_points_update.require(http_exception=403)
def points_update(id):
    controller = app.controllers.points_controller.PointsController()
    return controller.update(id)


@GisApp.route('/powerlines', methods=['GET'])
def powerlines():
    controller = app.controllers.powerlines_controller.PowerlinesController()
    return controller.index()


@GisApp.route('/transnet')
def transnet():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.index()


@GisApp.route('/transnet/stations_info')
def transnet_stations_info():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.stations_info()


@GisApp.route('/transnet/export')
def transnet_export():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.export_xml()


@GisApp.route('/transnet/export_xml')
def transnet_export_xml():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.export_xml()


@GisApp.route('/transnet/export_csv')
def transnet_export_csv():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.export_csv()


@GisApp.route('/transnet/export_countries_xml')
def transnet_export_countries_xml():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.export_countries_xml()


@GisApp.route('/transnet/export_countries_csv')
def transnet_export_countries_csv():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.export_countries_csv()


@GisApp.route('/transnet/evaluations')
def transnet_evaluations():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.evaluations()


@GisApp.route('/transnet/matlab_scripts')
def transnet_matlab_scripts():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.matlab_scripts()


@GisApp.route('/transnet/create_download_user', methods=['POST'])
def create_download_user():
    controller = app.controllers.transnet_controller.TransnetController()
    return controller.create_download_user()


@GisApp.route('/contribute/lines')
def contribute_lines():
    controller = ContributionController()
    return controller.get_lines()


@GisApp.route('/contribute/stations')
def contribute_stations():
    controller = ContributionController()
    return controller.get_stations()


@GisApp.route('/relations')
def relations():
    controller = app.controllers.relations_controller.RelationsController()
    return controller.index()


@GisApp.route('/relations/export')
def relations_export():
    controller = app.controllers.relations_controller.RelationsController()
    return controller.export()


@GisApp.route('/admin/login')
def admin_login():
    controller = app.controllers.admin.application_controller.ApplicationController()
    return controller.login()


@GisApp.route('/gallery')
def gallery_index():
    controller = app.controllers.gallery_controller.GalleryController()
    return controller.index()


@GisApp.route('/gallery/data')
def gallery_data():
    controller = app.controllers.gallery_controller.GalleryController()
    response = controller.data()
    # response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@GisApp.route('/gallery/thumb/<path:path>')
def gallery_thumb(path):
    controller = app.controllers.gallery_controller.GalleryController()
    return controller.thumb(path)


@GisApp.route('/admin/do_login')
def admin_do_login():
    return google.authorize(callback=url_for('authorized', _external=True))


@GisApp.route('/admin/login_app')
def admin_login_app():
    access_token = request.args.get("access_token")
    if access_token is None:
        return "No access token provided", 400

    email = validate_token(access_token)

    if email is None:
        return "Invalid Id Token", 400

    user = app.models.user.User.query.filter_by(email=email).first()

    if user is None:
        return 'Your user is not part of a system'
    else:
        login_user(user)
        # Tell Flask-Principal the identity changed
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(user.id))

        return "OK"


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
        next = session["next"]
        if (next):
            return redirect(next)
        else:
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
@app.permissions.admin_points.require(http_exception=403)
def admin_points():
    controller = app.controllers.admin.points_controller.PointsController()
    return controller.index()


@GisApp.route('/admin/points/new')
@login_required
@app.permissions.admin_points_new.require(http_exception=403)
def admin_points_new():
    controller = app.controllers.admin.points_controller.PointsController()
    return controller.new()


@GisApp.route('/admin/points/create', methods=['POST'])
##@login_required
##@app.permissions.admin_points_create.require(http_exception=403)
def admin_points_create():
    controller = app.controllers.admin.points_controller.PointsController()
    return controller.create()


@GisApp.route('/admin/points/edit/<id>')
@login_required
@app.permissions.admin_points_edit.require(http_exception=403)
def admin_points_edit(id):
    controller = app.controllers.admin.points_controller.PointsController()
    return controller.edit(id)


@GisApp.route('/admin/points/update/<id>', methods=['POST'])
@login_required
@app.permissions.admin_points_update.require(http_exception=403)
def admin_points_update(id):
    controller = app.controllers.admin.points_controller.PointsController()
    return controller.update(id)


@GisApp.route('/admin/points/delete/<id>')
@login_required
@app.permissions.admin_points_delete.require(http_exception=403)
def admin_points_delete(id):
    controller = app.controllers.admin.points_controller.PointsController()
    return controller.delete(id)


@GisApp.route('/admin/powerlines')
@login_required
@app.permissions.admin_powerlines.require(http_exception=403)
def admin_powerlines():
    controller = app.controllers.admin.powerlines_controller.PowerlinesController()
    return controller.index()


@GisApp.route('/admin/powerlines/new')
@login_required
@app.permissions.admin_powerlines_new.require(http_exception=403)
def admin_powerlines_new():
    controller = app.controllers.admin.powerlines_controller.PowerlinesController()
    return controller.new()


@GisApp.route('/admin/powerlines/create', methods=['POST'])
@login_required
@app.permissions.admin_powerlines_create.require(http_exception=403)
def admin_powerlines_create():
    controller = app.controllers.admin.powerlines_controller.PowerlinesController()
    return controller.create()


@GisApp.route('/admin/powerlines/edit/<id>', methods=['GET'])
@login_required
@app.permissions.admin_powerlines_edit.require(http_exception=403)
def admin_powerlines_edit(id):
    controller = app.controllers.admin.powerlines_controller.PowerlinesController()
    return controller.edit(id)


@GisApp.route('/admin/powerlines/update/<id>', methods=['POST'])
@login_required
@app.permissions.admin_powerlines_update.require(http_exception=403)
def admin_powerlines_update(id):
    controller = app.controllers.admin.powerlines_controller.PowerlinesController()
    return controller.update(id)


@GisApp.route('/admin/powerlines/delete/<id>', methods=['GET'])
@login_required
@app.permissions.admin_powerlines_delete.require(http_exception=403)
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


@GisApp.route('/admin/users/edit/<id>')
@login_required
def admin_users_edit(id):
    controller = app.controllers.admin.users_controller.UsersController()
    return controller.edit(id)


@GisApp.route('/admin/users/update/<id>', methods=['POST'])
@login_required
def admin_users_update(id):
    controller = app.controllers.admin.users_controller.UsersController()
    return controller.update(id)


@GisApp.route('/admin/users/delete/<id>')
@login_required
def admin_users_delete(id):
    controller = app.controllers.admin.users_controller.UsersController()
    return controller.delete(id)


@GisApp.route('/submissions/create', methods=['POST'])
def submissions_create():
    controller = app.controllers.submissions_controller.SubmissionsController()
    return controller.create()

@GisApp.route('/submissions/create_by_webapp', methods=['POST'])
@login_required
def submissions_create_by_webapp():
    controller = app.controllers.submissions_controller.SubmissionsController()
    return controller.create_by_webapp()


@GisApp.route('/admin/submissions')
@login_required
def submissions_index():
    controller = app.controllers.admin.submissions_controller.SubmissionsController()
    return controller.index()


@GisApp.route('/admin/submissions/revise/<id>')
@login_required
def submissions_revise(id):
    controller = app.controllers.admin.submissions_controller.SubmissionsController()
    return controller.revise(id)


@GisApp.route('/admin/submissions/accept_submission/<id>', methods=["POST"])
@login_required
def submissions_accept_submission(id):
    controller = app.controllers.admin.submissions_controller.SubmissionsController()
    return controller.accept_submission(id)


@GisApp.route('/admin/submissions/merge_new/<id>', methods=["POST"])  # is not used at the moment
@login_required
def submissions_merge_new(id):
    controller = app.controllers.admin.submissions_controller.SubmissionsController()
    return controller.merge_new(id)


@GisApp.route('/admin/submissions/merge_existing/<id>', methods=["POST"])
@login_required
def _submissions_merge_existing(id):
    controller = app.controllers.admin.submissions_controller.SubmissionsController()
    return controller.merge_existing(id)


@GisApp.route('/admin/submissions/merge/<id>', methods=['POST'])
@login_required
def submissions_merge(id):
    controller = app.controllers.admin.submissions_controller.SubmissionsController()
    return controller.merge(id)


@GisApp.route('/admin/submissions/reject/<id>', methods=['GET'])
@login_required
def submissions_reject(id):
    controller = app.controllers.admin.submissions_controller.SubmissionsController()
    return controller.reject_submission(id)


@GisApp.route('/admin/submissions/delete/<id>', methods=['GET'])
@login_required
@app.permissions.admin_points_delete.require(http_exception=403)
def submissions_delete(id):
    controller = app.controllers.admin.submissions_controller.SubmissionsController()
    return controller.delete(id)


@GisApp.route('/admin/transnet_users')
@login_required
def transnet_users():
    controller = TransnetUsersController()
    return controller.index()


@GisApp.route('/admin/transnet_users/delete/<id>', methods=['GET'])
@login_required
def transnet_users_delete(id):
    controller = TransnetUsersController()
    return controller.delete(id)


@GisApp.route('/admin/transnet_logs')
@login_required
def transnet_logs():
    controller = TransnetLogsController()
    return controller.index()


@GisApp.route('/admin/transnet_logs/delete/<id>', methods=['GET'])
@login_required
def transnet_logs_delete(id):
    controller = TransnetLogsController()
    return controller.delete(id)


@GisApp.errorhandler(500)
def internal_error(error):
    controller = app.controllers.application_controller.ApplicationController()
    return controller.page500()


@GisApp.errorhandler(403)
def internal_error(error):
    controller = app.controllers.application_controller.ApplicationController()
    return controller.page403()


def validate_token(id_token):
    '''Verifies that an access-token is valid and
    meant for this app.

    Returns None on fail, and an e-mail on success'''
    h = Http()
    resp, cont = h.request("https://www.googleapis.com/oauth2/v1/tokeninfo?id_token=" + id_token, "GET")

    if not resp['status'] == '200':
        return None

    try:
        data = json.loads(cont)
    except TypeError:
        # Running this in Python3
        # httplib2 returns byte objects
        data = json.loads(cont.decode())

    if (data['audience'] != GisApp.config.get('GOOGLE_CLIENT_ID')):
        raise

    if (data['issued_to'] != "498377614550-ocmo2vu3euufkmekbqvf5kdpjo9el02c.apps.googleusercontent.com"):
        raise

    if (data['expires_in'] <= 0):
        raise

    return data['email']
