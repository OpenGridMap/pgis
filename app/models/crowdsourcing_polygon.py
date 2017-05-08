from app import db
from app import GisApp
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

class CrowdsourcingPolygon(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    geom = db.Column(Geometry('POLYGON'))

    def serialize(self):
        return {
            'id': self.id,
            'latlng': list(to_shape(self.geom).exterior.coords)
        }