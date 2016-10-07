from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON

from app import db


class TransnetStation(db.Model):
    __tablename__ = 'transnet_station'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    geom = db.Column(Geometry('POLYGON'))
    tags = db.Column(JSON, nullable=True)
    lat = db.Column(db.NUMERIC, nullable=True)
    lon = db.Column(db.NUMERIC, nullable=True)
    name = db.Column(db.String, nullable=True)
    nominal_power = db.Column(db.String, nullable=True)
    length = db.Column(db.NUMERIC, nullable=True)
    osm_id = db.Column(db.INTEGER, nullable=True)
    voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    type = db.Column(db.String, nullable=True)
    relation_id = db.Column(db.Integer, db.ForeignKey('transnet_relation.id'))
    relation = db.relationship('TransnetRelation', primaryjoin='TransnetRelation.id==TransnetStation.relation_id',
                               back_populates='stations')

    def shape(self):
        return to_shape(self.geom)
