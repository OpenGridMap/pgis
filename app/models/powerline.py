from app import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import JSON

class Powerline(db.Model):
    id 	 = db.Column(db.Integer, primary_key=True)
    geom = db.Column(Geometry('LINESTRING'))
    properties = db.Column(JSON)

    def serialize(self):
        return list(self.shape().coords)

    def shape(self):
        return to_shape(self.geom)

    @property
    def latlngs(self):
        return ', '.join(list(map(lambda tuple: str(tuple[0]) + ' ' + str(tuple[1]), list(self.shape().coords))))
