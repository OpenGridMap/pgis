from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import JSON

from app import db


class TransnetPowerline(db.Model):
    __tablename__ = 'transnet_powerline'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    geom = db.Column(Geometry('LINESTRING'))
    properties = db.Column(JSON)

    def serialize(self):
        return {"id": self.id, "latlngs": list(self.shape().coords), "tags": self.properties["voltage"]}

    def shape(self):
        return to_shape(self.geom)

    @property
    def latlngs(self):
        return ', '.join(list(map(lambda tuple: str(tuple[0]) + ' ' + str(tuple[1]), list(self.shape().coords))))