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
    srs_geom = db.Column(Geometry('LINESTRING'), nullable=True)
    tags = db.Column(JSON, nullable=True)
    voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    type = db.Column(db.String, nullable=True)
    nodes = db.Column(ARRAY(db.BIGINT), nullable=True)
    lat = db.Column(db.NUMERIC, nullable=True)
    lon = db.Column(db.NUMERIC, nullable=True)
    cables = db.Column(db.INTEGER, nullable=True)
    name = db.Column(db.String, nullable=True)
    length = db.Column(db.NUMERIC, nullable=True)
    osm_id = db.Column(db.INTEGER, nullable=True)
    osm_replication = db.Column(db.Integer, nullable=True, default=1)

    def shape(self):
        return to_shape(self.geom)
