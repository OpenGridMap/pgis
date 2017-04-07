from flask.ext.login import current_user
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response

class AjaxLoginController:

    def is_authenticated(self):
        user = {}
        #if current_user.is_authenticated:
        #    user['is_authenticated'] = 1
        #else:
        #    user['is_authenticated'] = 0
        user['is_authenticated'] = current_user.is_authenticated()
        return Response(json.dumps(user),  mimetype='application/json')