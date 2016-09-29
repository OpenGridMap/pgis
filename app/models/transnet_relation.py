from geoalchemy2 import Geography
from geoalchemy2 import func
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import ARRAY

from app import db
from app.models.transnet_powerline import TransnetPowerline
from app.models.transnet_station import TransnetStation


class TransnetRelation(db.Model):
    __tablename__ = 'transnet_relation'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    ref = db.Column(db.String, nullable=True)
    powerlines = db.relationship('TransnetPowerline', back_populates='relation')
    stations = db.relationship('TransnetStation', back_populates='relation')

    def serialize(self):
        return {"id": self.id, }

    @staticmethod
    def with_points_and_lines_in_bounds(bounds):

        powerlines = TransnetPowerline.query.filter(
            func.ST_Intersects(
                func.ST_MakeEnvelope(
                    bounds[1],
                    bounds[0],
                    bounds[3],
                    bounds[2]
                ),
                cast(TransnetPowerline.geom, Geography)
            )
        ).all()

        stations = TransnetStation.query.filter(
            func.ST_Intersects(
                func.ST_MakeEnvelope(
                    bounds[1],
                    bounds[0],
                    bounds[3],
                    bounds[2]
                ),
                cast(TransnetStation.geom, Geography)
            )
        ).all()

        return TransnetRelation.prepare_relations_for_export(powerlines, stations)

    @staticmethod
    def relations_for_export(relation_ids):

        powerlines = TransnetPowerline.query.filter(
            TransnetPowerline.relation_id.in_(relation_ids)
        ).all()

        stations = TransnetStation.query.filter(
            TransnetStation.relation_id.in_(relation_ids)
        ).all()

        return TransnetRelation.prepare_relations_for_export(powerlines, stations)

    @staticmethod
    def prepare_relations_for_export(powerlines, stations):

        relations = {}

        for powerline in powerlines:
            if powerline.relation_id not in relations:
                relations[powerline.relation_id] = {
                    'id': powerline.relation_id,
                    'properties': {
                        'osmid': powerline.relation_id,
                        'tags': {},
                    },
                    'points': [],
                    'powerlines': []
                }
            relations[powerline.relation_id]['powerlines'].append({
                'id': powerline.osm_id,
                'latlngs': list(powerline.shape().coords),
                'properties': {
                    'tags': powerline.tags,
                },
            })

        for station in stations:
            if station.relation_id not in relations:
                relations[station.relation_id] = {
                    'id': station.relation_id,
                    'properties': {
                        'osmid': station.relation_id,
                    },
                    'points': [],
                    'powerlines': []
                }
            relations[station.relation_id]['points'].append({
                'id': station.osm_id,
                'latlng': [station.lat, station.lon],
                'latlngs': list(station.shape().exterior.coords),
                'properties': {
                    'tags': station.tags,
                    'osmid': station.osm_id,
                },
            })

        return relations
