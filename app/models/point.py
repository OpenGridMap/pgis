from app import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import JSON

class Point(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    geom = db.Column(Geometry('POINT'))
    properties = db.Column(JSON)
    revised = db.Column(db.Boolean)
    approved = db.Column(db.Boolean)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    submission = db.relationship('Submission', back_populates='points')
    merged_to = db.Column(db.Integer, db.ForeignKey('point.id'))
    pictures = db.relationship('Picture')

    def serialize(self):
        return { 'id': self.id, 'latlng': [self.shape().x, self.shape().y], 'tags' : self.properties.get('tags', {}), 'pictures' : list(map((lambda p: p.serialize()), self.pictures)) }

    def serialize_with_properties(self):
        return { 'id': self.id, 'latlng': [self.shape().x, self.shape().y], 'properties' : self.properties, 'pictures' : list(map((lambda p: p.serialize()), self.pictures)) }

    def serialize_for_export(self):
        return {'type': 'Feature', 'id': self.id, 'coordinates': [self.shape().x, self.shape().y], 'properties' : self.properties }
    
    def shape(self):
        return to_shape(self.geom)

    @property
    def latitude(self):
        return self.shape().x

    @property
    def longitude(self):
        return self.shape().y
