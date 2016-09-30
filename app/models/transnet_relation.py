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
    def make_base_relation(relation_id):
        return {
            'id': relation_id,
            'properties': {
                'osmid': relation_id,
                'tags': {
                    'osmid': relation_id,
                },
            },
            'points': [],
            'powerlines': []
        }

    @staticmethod
    def prepare_relations_for_export(powerlines, stations):

        relations = {}

        for powerline in powerlines:
            if powerline.relation_id not in relations:
                relations[powerline.relation_id] = TransnetRelation.make_base_relation(powerline.relation_id)

            tags = powerline.tags
            tags['country'] = powerline.country
            tags['lat'] = powerline.lat
            tags['lon'] = powerline.lon
            tags['name'] = powerline.name
            tags['length'] = powerline.length
            tags['osm_id'] = powerline.osm_id
            tags['voltage'] = powerline.voltage
            tags['type'] = powerline.type
            tags['cables'] = powerline.cables
            tags['relation_id'] = powerline.relation_id

            relations[powerline.relation_id]['powerlines'].append({
                'id': powerline.osm_id,
                'latlngs': list(powerline.shape().coords),
                'properties': {
                    'tags': tags,
                    'osmid': powerline.osm_id,
                },
            })

        for station in stations:
            if station.relation_id not in relations:
                relations[station.relation_id] = TransnetRelation.make_base_relation(station.relation_id)

            tags = station.tags
            tags['country'] = station.country
            tags['lat'] = station.lat
            tags['lon'] = station.lon
            tags['name'] = station.name
            tags['length'] = station.length
            tags['osm_id'] = station.osm_id
            tags['voltage'] = station.voltage
            tags['type'] = station.type
            tags['relation_id'] = station.relation_id

            relations[station.relation_id]['points'].append({
                'id': station.osm_id,
                'latlng': [station.lat, station.lon],
                'latlngs': list(station.shape().exterior.coords),
                'properties': {
                    'tags': tags,
                    'osmid': station.osm_id,
                },
            })

        return relations
