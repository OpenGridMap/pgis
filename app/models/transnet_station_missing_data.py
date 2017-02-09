import random

from geoalchemy2 import Geography
from geoalchemy2 import Geometry
from geoalchemy2 import func
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON

from app import db


class TransnetPowerStationMissingData(db.Model):
    __tablename__ = 'transnet_station_missing_data'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    geom = db.Column(Geometry('POLYGON'))
    tags = db.Column(JSON, nullable=True)
    lat = db.Column(db.NUMERIC, nullable=True)
    lon = db.Column(db.NUMERIC, nullable=True)
    name = db.Column(db.String, nullable=True)
    length = db.Column(db.NUMERIC, nullable=True)
    osm_id = db.Column(db.INTEGER, nullable=True)
    voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    type = db.Column(db.String, nullable=True)
    estimated_voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    missing_connection = db.Column(db.BOOLEAN, nullable=False, default=False)

    @staticmethod
    def get_filtered_stations(bounds):
        power_stations_sample = db.session.query(TransnetPowerStationMissingData.id).filter(
            func.ST_Intersects(
                func.ST_MakeEnvelope(
                    bounds[1],
                    bounds[0],
                    bounds[3],
                    bounds[2]
                ),
                cast(TransnetPowerStationMissingData.geom, Geography)
            )
        ).all()

        if len(power_stations_sample) > 5000:
            power_stations_sample = random.sample(power_stations_sample, 5000)

        power_stations = TransnetPowerStationMissingData.query.filter(
            TransnetPowerStationMissingData.id.in_(power_stations_sample)).all()

        return list(map(lambda s: s.serialize(), power_stations))

    def serialize(self):
        return {"id": self.id, "latlng": [self.lat, self.lon], "tags": self.tags, "lat": self.lat,
                "lon": self.lon, "osm_id": self.osm_id, "estimated_voltage": self.estimated_voltage,
                "missing_connection": self.missing_connection,"voltage": self.voltage,
                "type": self.type}
