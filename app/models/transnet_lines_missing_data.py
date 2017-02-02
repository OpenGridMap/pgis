import random

from geoalchemy2 import Geography
from geoalchemy2 import Geometry
from geoalchemy2 import func
from geoalchemy2.shape import to_shape
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON

from app import db


class TransnetPowerLineMissingData(db.Model):
    __tablename__ = 'transnet_line_missing_data'
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
    estimated_voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    estimated_cables = db.Column(ARRAY(db.INTEGER), nullable=True)

    @staticmethod
    def get_filtered_relations(bounds):
        powerlines_sample = db.session.query(TransnetPowerLineMissingData.id).filter(
            func.ST_Intersects(
                func.ST_MakeEnvelope(
                    bounds[1],
                    bounds[0],
                    bounds[3],
                    bounds[2]
                ),
                cast(TransnetPowerLineMissingData.geom, Geography)
            )
        ).all()

        if len(powerlines_sample) > 2000:
            powerlines_sample = random.sample(powerlines_sample, 2000)

        powerlines = TransnetPowerLineMissingData.query.filter(
            TransnetPowerLineMissingData.id.in_(powerlines_sample)).all()

        return list(map(lambda powerline: powerline.serialize(), powerlines))

    def serialize(self):
        return {"id": self.id, "latlngs": list(self.shape().coords), "tags": self.tags}

    def shape(self):
        return to_shape(self.geom)

    @property
    def latlngs(self):
        return ', '.join(list(map(lambda tuple: str(tuple[0]) + ' ' + str(tuple[1]), list(self.shape().coords))))
