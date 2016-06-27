from flask import render_template
from app.models.user import User

class RankingController():

    def index(self):
        users = User.query.order_by(User.activity_points.desc()).limit(10).paginate(1)
        return render_template('ranking.html', users=users)