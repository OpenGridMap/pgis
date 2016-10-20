from geoalchemy2 import Geography
from geoalchemy2 import func
from sqlalchemy import cast
from sqlalchemy import or_
from sqlalchemy.orm import load_only
from sqlalchemy.sql.expression import any_, all_

from app import db
from app.models.transnet_powerline import TransnetPowerline
from app.models.transnet_station import TransnetStation


class TransnetRelation(db.Model):
    __tablename__ = 'transnet_relation'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    voltage = db.Column(db.INTEGER, nullable=True)
    ref = db.Column(db.String, nullable=True)
    powerlines = db.relationship(TransnetPowerline, back_populates='relation')
    stations = db.relationship(TransnetStation, back_populates='relation')

    def serialize(self):
        return {"id": self.id, }

    @staticmethod
    def with_points_and_lines_in_bounds(bounds, voltages, countries):

        powerlines_qry = TransnetPowerline.query

        stations_qry = TransnetStation.query

        if bounds:
            powerlines_qry = powerlines_qry.filter(
                func.ST_Intersects(
                    func.ST_MakeEnvelope(
                        bounds[1],
                        bounds[0],
                        bounds[3],
                        bounds[2]
                    ),
                    cast(TransnetPowerline.geom, Geography)
                )
            )
            stations_qry = stations_qry.filter(
                func.ST_Intersects(
                    func.ST_MakeEnvelope(
                        bounds[1],
                        bounds[0],
                        bounds[3],
                        bounds[2]
                    ),
                    cast(TransnetStation.geom, Geography)
                )
            )

        if countries:
            powerlines_qry = powerlines_qry.filter(TransnetPowerline.country.in_(countries))
            stations_qry = stations_qry.filter(TransnetStation.country.in_(countries))

        if voltages:
            powerlines_qry = powerlines_qry.join(TransnetRelation).filter(
                or_(TransnetPowerline.voltage.overlap(voltages), TransnetRelation.voltage.in_(voltages)))
            stations_qry = stations_qry.join(TransnetRelation).filter(
                or_(TransnetStation.voltage.overlap(voltages), TransnetRelation.voltage.in_(voltages)))

        powerlines = powerlines_qry.options(load_only("relation_id", )).distinct()
        stations = stations_qry.options(load_only("relation_id", )).distinct()

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
    def make_base_relation(relation):
        return {
            'id': relation.id,
            'properties': {
                'osmid': relation.id,
                'tags': {
                    'osmid': relation.id,
                    'warning': 'NO OSM ID',
                    'name': relation.name,
                    'ref': relation.ref,
                    'voltage': relation.voltage,
                    'country': relation.country
                },
            },
            'points': [],
            'powerlines': []
        }

    @staticmethod
    def prepare_relations_for_export(powerlines, stations):

        relations = {}

        relation_ids = []

        for powerline in powerlines:
            if powerline.relation_id not in relation_ids:
                relation_ids.append(powerline.relation_id)

        for station in stations:
            if station.relation_id not in relation_ids:
                relation_ids.append(station.relation_id)

        relations_query = TransnetRelation.query.filter(
            TransnetRelation.id.in_(relation_ids)
        ).all()

        for relation in relations_query:
            for powerline in relation.powerlines:
                if powerline.relation_id not in relations:
                    relations[powerline.relation_id] = TransnetRelation.make_base_relation(relation)

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
            for station in relation.stations:
                if station.relation_id not in relations:
                    relations[station.relation_id] = TransnetRelation.make_base_relation(relation)

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

    @staticmethod
    def get_evaluations(countries):
        powerline_tags = ['line', 'cable', 'minor_line']
        station_tags = ['substation', 'station', 'sub_station']
        plant_tags = ['plant', 'generator']

        countries_stats = {}
        for country in countries:
            country_stat = {
                'all_line_length': 0,
                'plants_count': 0,
                'substations_count': 0,
                'powerlines_counts': 0,
                'length_by_voltages': {}
            }
            try:


                country_stat['all_line_length'] = \
                    db.session.query(func.sum(TransnetPowerline.length).label('sum_line')).filter(
                        TransnetPowerline.country == country)[0][0] / 1000
                country_stat['plants_count'] = db.session.query(func.count(TransnetStation.id)).filter(
                    TransnetStation.country == country).filter(
                    TransnetStation.type.in_(plant_tags))[0][0]
                country_stat['substations_count'] = db.session.query(func.count(TransnetStation.id)).filter(
                    TransnetStation.country == country).filter(
                    TransnetStation.type.in_(station_tags))[0][0]
                country_stat['powerlines_counts'] = db.session.query(func.count(TransnetPowerline.id)).filter(
                    TransnetPowerline.country == country).filter(
                    TransnetPowerline.type.in_(powerline_tags))[0][0]
                country_stat['length_by_voltages'] = {}
                voltages = db.session.query(func.unnest(TransnetPowerline.voltage)).filter(
                    TransnetPowerline.country == country).distinct()
                for voltage in voltages:
                    country_stat['length_by_voltages'][voltage[0]] = []
                    length_shared = db.session.query(func.sum(TransnetPowerline.length).label('sum_line')).filter(
                        TransnetPowerline.country == country).filter(voltage == any_(TransnetPowerline.voltage))
                    if length_shared.count() and length_shared[0][0]:
                        country_stat['length_by_voltages'][voltage[0]].append(length_shared[0][0] / 1000)
                    else:
                        country_stat['length_by_voltages'][voltage[0]].append(0)

                    length_single_value = db.session.query(func.sum(TransnetPowerline.length).label('sum_line')).filter(
                        TransnetPowerline.country == country).filter(voltage == all_(TransnetPowerline.voltage))
                    if length_single_value.count() and length_single_value[0][0]:
                        country_stat['length_by_voltages'][voltage[0]].append(length_single_value[0][0] / 1000)
                    else:
                        country_stat['length_by_voltages'][voltage[0]].append(0)
            except Exception as ex:
                pass
            countries_stats[country] = country_stat

        if len(countries) > 1:
            country_stat = {}
            country_stat['all_line_length'] = sum([cn['all_line_length'] for cn in countries_stats.values()])
            country_stat['plants_count'] = sum([cn['plants_count'] for cn in countries_stats.values()])
            country_stat['substations_count'] = sum([cn['substations_count'] for cn in countries_stats.values()])
            country_stat['powerlines_counts'] = sum([cn['powerlines_counts'] for cn in countries_stats.values()])
            country_stat['length_by_voltages'] = {}
            for cn in countries_stats.values():
                for voltage in cn['length_by_voltages']:
                    if voltage in country_stat['length_by_voltages'].keys():
                        country_stat['length_by_voltages'][voltage][0] += cn['length_by_voltages'][voltage][0]
                        country_stat['length_by_voltages'][voltage][1] += cn['length_by_voltages'][voltage][1]
                    else:
                        country_stat['length_by_voltages'][voltage] = []
                        country_stat['length_by_voltages'][voltage].append(cn['length_by_voltages'][voltage][0])
                        country_stat['length_by_voltages'][voltage].append(cn['length_by_voltages'][voltage][1])

            countries_stats['aaa'] = country_stat

        return countries_stats
