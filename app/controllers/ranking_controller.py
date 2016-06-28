from flask import render_template
from app.models.user import User
from app import db

class RankingController():

    def index(self):
        users = db.session.query(User).order_by(User.activity_points.desc()).limit(10).all()
        return render_template('ranking.html', users=users)