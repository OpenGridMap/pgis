from app import db
from sqlalchemy.dialects.postgresql import JSON

class Submission(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    point_data = db.Column(JSON)
    revised = db.Column(db.Boolean)
