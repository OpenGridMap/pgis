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
        point = points[0]
        properties = point['properties']['tags']

        altitude = self.get_value_from_properties(properties, 'altitude')
        power_element_tags = self.get_value_from_properties(properties, 'power_element_tags')
        timestamp = self.get_value_from_properties(properties, 'timestamp')

        serialized_submission = {
            'id': self.id,
            'latlng': point['latlng'],
            'image_src': point['pictures'][0]['filepath'],
            'altitude': altitude,
            'power_element_tag': power_element_tags,
            'timestamp': timestamp,
            'revised': point['revised'],
            'approved': point['approved']
        }

        return serialized_submission

    @staticmethod
    def get_value_from_properties(properties, key):
        try:
            return properties[key]
        except KeyError as e:
            return ''

    def images(self):
        pass
