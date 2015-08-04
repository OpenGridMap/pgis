from app import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import JSON

class Point(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    geom = db.Column(Geometry('POINT'))
    properties = db.Column(JSON)
    revised = db.Column(db.Boolean)
    submission_id = db.Column(db.String)

    def serialize(self):
        point = self.shape()
        return { 'id': self.id, 'latlng': [self.shape().x, self.shape().y], 'tags' : self.properties.get('tags', {}) } 
    
    def shape(self):
        return to_shape(self.geom)

    @property
    def latitude(self):
        return self.shape().x

    @property
    def longitude(self):
        return self.shape().y
