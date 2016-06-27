from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from flask.ext.login import LoginManager, current_user
from app import db
from app.models.user import User

class BonusSystemController:
    def index(self):
        if request.args.get('email') is None:
            return Response(json.dumps([]), mimetype='application/json')
        email = request.args.get('email')
        activity_points = User.query.filter(User.email==email).first()
        activity_points = activity_points.get_acitivity_points()
        return Response(json.dumps(activity_points),  mimetype='application/json')