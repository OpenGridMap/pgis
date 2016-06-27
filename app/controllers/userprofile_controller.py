from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from flask.ext.login import LoginManager, current_user
from app import db
from app.models.user import User
from app.models.picture import Picture

class UserprofileController():

    def index(self):
        user = User.query.get(current_user.id)
        ranking = User.query.filter(User.activity_points < user.activity_points).count()
        pictures = Picture.query.filter(Picture.user_id==current_user.id)
        return render_template('userprofile.html', user=user, pictures=pictures, ranking=ranking)