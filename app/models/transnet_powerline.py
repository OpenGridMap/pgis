from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON

from app import db


class TransnetPowerline(db.Model):
    __tablename__ = 'transnet_powerline'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    geom = db.Column(Geometry('LINESTRING'))
    tags = db.Column(JSON, nullable=True)
    raw_geom = db.Column(db.String, nullable=True)
    voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    type = db.Column(db.String, nullable=True)
    nodes = db.Column(ARRAY(db.INTEGER), nullable=True)
    lat = db.Column(db.INTEGER, nullable=True)
    lon = db.Column(db.INTEGER, nullable=True)
    cables = db.Column(db.INTEGER, nullable=True)
    name = db.Column(db.String, nullable=True)
    length = db.Column(db.INTEGER, nullable=True)
    osm_id = db.Column(db.INTEGER, nullable=True)
    relation_id = db.Column(db.Integer, db.ForeignKey('transnet_relation.id'))

    def serialize(self):
        return {"id": self.id, "latlngs": list(self.shape().coords)}

    def shape(self):
        return to_shape(self.geom)

    @property
    def latlngs(self):
        return ', '.join(list(map(lambda tuple: str(tuple[0]) + ' ' + str(tuple[1]), list(self.shape().coords))))
