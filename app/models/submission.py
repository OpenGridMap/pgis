from app import db
from sqlalchemy.dialects.postgresql import JSON

class Submission(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.BigInteger)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='submissions')
    number_of_points = db.Column(db.Integer)
    revised = db.Column(db.Boolean)
    approved = db.Column(db.Boolean)
    points = db.relationship('Point', back_populates='submission')

    def serialize(self):
        return { 'id': self.id,  "points" : list(map((lambda p: p.serialize()), self.points))}

    def serialize_for_mobileapp(self):
        return { 'id': self.id, 'user_id': self.user_id, 'user': self.user.email.partition("@")[0][0:6],  "points" : list(map((lambda p: p.serialize_with_properties()), self.points))}

    def serialize_for_gallery(self):
        points = list(map((lambda p: p.serialize_for_gallery()), self.points))

        return {
            'id': self.id,
            'latlng': points[0]['latlng'],
            'image_src': points[0]['pictures'][0]['filepath'],
            # 'accuracy': points[0]['properties']['accuracy'],
            'altitude': points[0]['properties']['altitude'],
            'power_element_tag': points[0]['properties']['power_elements_tags'],
            'timestamp': points[0]['properties']['timestamp'],
            'revised': points[0]['revised'],
            'approved': points[0]['approved']
        }

    def images(self):
        pass
