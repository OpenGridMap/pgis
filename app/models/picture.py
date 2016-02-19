from app import db

class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    point_id = db.Column(db.Integer, db.ForeignKey('point.id'))
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filepath = db.Column(db.String)

    def serialize(self):
        return { 'filepath' : self.filepath }