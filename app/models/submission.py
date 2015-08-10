from app import db
from sqlalchemy.dialects.postgresql import JSON

class Submission(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    number_of_points = db.Column(db.Integer)
    revised = db.Column(db.Boolean)
    points = db.relationship('Point')

    def images(self):
        pass
