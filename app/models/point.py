from app import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import JSON

class Point(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    geom = db.Column(Geometry('POINT'))
    properties = db.Column(JSON)

    def serialize(self):
        point = self.shape()
        return { 'name': self.name, 'latlng': [self.shape().x, self.shape().y] } 
    
    def shape(self):
        return to_shape(self.geom)

    @property
    def latitude(self):
        return self.shape().x

    @property
    def longitude(self):
        return self.shape().y
