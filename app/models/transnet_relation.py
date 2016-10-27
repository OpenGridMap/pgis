from os.path import join, dirname

from geoalchemy2 import Geography
from geoalchemy2 import func
from sqlalchemy import cast
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import any_, all_

from app import db
from app.models.transnet_powerline import TransnetPowerline
from app.models.transnet_relation_powerline import TransnetRelationPowerline
from app.models.transnet_relation_station import TransnetRelationStation
from app.models.transnet_station import TransnetStation


class TransnetRelation(db.Model):
    __tablename__ = 'transnet_relation'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    voltage = db.Column(db.INTEGER, nullable=True)
    ref = db.Column(db.String, nullable=True)
    powerlines = db.relationship('TransnetPowerline', secondary='transnet_relation_powerline',
                                 backref=db.backref('relations'))
    stations = db.relationship('TransnetStation', secondary='transnet_relation_station',
                               backref=db.backref('relations'))

    def serialize(self):
        return {"id": self.id, }

    # Let this be here
    @staticmethod
    def fake():
        TransnetRelationPowerline.query.all()
        TransnetRelationStation.query.all()

    @staticmethod
    def get_filtered_relations(bounds, voltages, countries, zoom):

        powerlines_qry = TransnetPowerline.query

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

        if countries:
            powerlines_qry = powerlines_qry.filter(TransnetPowerline.country.in_(countries))

        if voltages:
            powerlines_qry = powerlines_qry.join(TransnetRelation).filter(
                or_(TransnetPowerline.voltage.overlap(voltages), TransnetRelation.voltage.in_(voltages)))

        powerline_relations = powerlines_qry.options(joinedload('relations')).all()

        return TransnetRelation.prepare_relations_for_export(powerline_relations, [], zoom)

    @staticmethod
    def relations_for_export(relation_ids):

        relations = TransnetRelation.query.filter(
            TransnetRelation.id.in_(relation_ids)
        ).all()

        return TransnetRelation.prepare_relations_for_export([], relations, None)

    @staticmethod
    def get_station_info(relation_id):

        relations = TransnetRelation.query.filter(
            TransnetRelation.id == relation_id
        ).all()

        return TransnetRelation.prepare_relations_for_export([], relations, None)

    @staticmethod
    def make_base_relation(relation):
        return {
            'id': relation.id,
            'length': 0,
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
    def prepare_relations_for_export(powerline_relations, relations_filtered, zoom):

        relations_to_export = {}

        relations_query = set()

        relations_query.update(relations_filtered)
        [relations_query.update([r for r in x.relations]) for x in powerline_relations]

        for relation in relations_query:
            for powerline in relation.powerlines:
                if relation.id not in relations_to_export:
                    relations_to_export[relation.id] = TransnetRelation.make_base_relation(relation)

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
                relations_to_export[relation.id]['length'] += powerline.length
                relations_to_export[relation.id]['powerlines'].append({
                    'id': powerline.osm_id,
                    'latlngs': list(powerline.shape().coords),
                    'properties': {
                        'tags': tags,
                        'osmid': powerline.osm_id,
                    },
                })
            for station in relation.stations:
                if relation.id not in relations_to_export:
                    relations_to_export[relation.id] = TransnetRelation.make_base_relation(relation)
                if not zoom or int(zoom) > 10:
                    tags = station.tags
                    tags['country'] = station.country
                    tags['lat'] = station.lat
                    tags['lon'] = station.lon
                    tags['name'] = station.name
                    tags['length'] = station.length
                    tags['osm_id'] = station.osm_id
                    tags['voltage'] = station.voltage
                    tags['type'] = station.type

                    relations_to_export[relation.id]['points'].append({
                        'id': station.osm_id,
                        'latlng': [station.lat, station.lon],
                        'latlngs': list(station.shape().exterior.coords),
                        'properties': {
                            'tags': tags,
                            'osmid': station.osm_id,
                        },
                    })
                else:
                    relations_to_export[relation.id]['hast_points'] = True

            relations_to_export[relation.id]['length'] = round(relations_to_export[relation.id]['length'])

        return relations_to_export

    @staticmethod
    def get_evaluations(countries):
        powerline_tags = ['line', 'cable', 'minor_line']
        station_tags = ['substation', 'station', 'sub_station']
        plant_tags = ['plant', 'generator']

        countries_stats = {}
        for country in countries:

            country_stat = {
                'all_line_length': 0,
                'all_line_length_s': 0,
                'plants_count': 0,
                'plants_count_s': 0,
                'substations_count': 0,
                'substations_count_s': 0,
                'length_by_voltages': {}
            }
            try:

                with open(join(dirname(__file__), '../../resources/europe/{0}/where_clause'.format(country))) as w_s:
                    where_clause = w_s.readline()
                scigrid_length_query = '''SELECT sum(s.length_m) AS length
                                          FROM scigrid_powerline s
                                          WHERE %s''' % where_clause
                country_stat['all_line_length_s'] = [round(x[0]) for x in db.engine.execute(scigrid_length_query)][
                                                        0] / 1000
                scigrid_station_count_query = '''SELECT count(*) as count
                                                FROM scigrid_station s
                                                WHERE s.type ~ 'station|substation|merge|sub_station' and %s''' % where_clause
                country_stat['substations_count_s'] = \
                    [x[0] for x in db.engine.execute(scigrid_station_count_query)][0]
                scigrid_plant_count_query = '''SELECT count(*) as count
                                                FROM scigrid_station s
                                                WHERE s.type ~ 'plant' and %s''' % where_clause
                country_stat['plants_count_s'] = [x[0] for x in db.engine.execute(scigrid_plant_count_query)][0]

                country_stat['all_line_length'] = \
                    db.session.query(func.sum(TransnetPowerline.length).label('sum_line')).filter(
                        TransnetPowerline.country == country)[0][0] / 1000
                country_stat['plants_count'] = db.session.query(func.count(TransnetStation.id)).filter(
                    TransnetStation.country == country).filter(
                    TransnetStation.type.in_(plant_tags))[0][0]
                country_stat['substations_count'] = db.session.query(func.count(TransnetStation.id)).filter(
                    TransnetStation.country == country).filter(
                    TransnetStation.type.in_(station_tags))[0][0]
                country_stat['length_by_voltages'] = {}
                voltages = db.session.query(func.unnest(TransnetPowerline.voltage)).filter(
                    TransnetPowerline.country == country).distinct()
                for voltage in voltages:
                    country_stat['length_by_voltages'][voltage[0]] = []
                    length_shared = db.session.query(func.sum(TransnetPowerline.length).label('sum_line')).filter(
                        TransnetPowerline.country == country).filter(TransnetPowerline.voltage.any(voltage[0]))
                    print(length_shared.count())
                    if length_shared.count() and length_shared[0][0]:
                        country_stat['length_by_voltages'][voltage[0]].append(length_shared[0][0] / 1000)
                    else:
                        country_stat['length_by_voltages'][voltage[0]].append(0)

                    scigrid_voltage_any = '''SELECT sum(s.length_m) as length
                                                    FROM scigrid_powerline s
                                                    WHERE s.voltage @> ARRAY[%s]::int[] and %s''' % \
                                          (voltage[0], where_clause)
                    scigrid_temp_voltage_any = [x[0] for x in db.engine.execute(scigrid_voltage_any)]

                    if len(scigrid_temp_voltage_any) and scigrid_temp_voltage_any[0]:
                        country_stat['length_by_voltages'][voltage[0]].append(scigrid_temp_voltage_any[0] / 1000)
                    else:
                        country_stat['length_by_voltages'][voltage[0]].append(0)

                    length_single_value = db.session.query(func.sum(TransnetPowerline.length).label('sum_line')).filter(
                        TransnetPowerline.country == country).filter(TransnetPowerline.voltage.all(voltage[0]))

                    if length_single_value.count() and length_single_value[0][0]:
                        country_stat['length_by_voltages'][voltage[0]].append(length_single_value[0][0] / 1000)
                    else:
                        country_stat['length_by_voltages'][voltage[0]].append(0)

                    scigrid_voltage_all = '''SELECT sum(s.length_m) as length
                                            FROM scigrid_powerline s
                                            WHERE s.voltage = ARRAY[%s]::int[] and %s''' % \
                                          (voltage[0], where_clause)
                    scigrid_temp_voltage_all = [x[0] for x in db.engine.execute(scigrid_voltage_all)]
                    if len(scigrid_temp_voltage_all) and scigrid_temp_voltage_all[0]:
                        country_stat['length_by_voltages'][voltage[0]].append(scigrid_temp_voltage_all[0] / 1000)
                    else:
                        country_stat['length_by_voltages'][voltage[0]].append(0)

            except Exception as ex:
                pass
            countries_stats[country] = country_stat

        if len(countries) > 1:
            country_stat = {}
            country_stat['all_line_length'] = sum([cn['all_line_length'] for cn in countries_stats.values()])
            country_stat['all_line_length_s'] = sum([cn['all_line_length_s'] for cn in countries_stats.values()])
            country_stat['plants_count'] = sum([cn['plants_count'] for cn in countries_stats.values()])
            country_stat['plants_count_s'] = sum([cn['plants_count_s'] for cn in countries_stats.values()])
            country_stat['substations_count'] = sum([cn['substations_count'] for cn in countries_stats.values()])
            country_stat['substations_count_s'] = sum([cn['substations_count_s'] for cn in countries_stats.values()])
            country_stat['length_by_voltages'] = {}
            for cn in countries_stats.values():
                for voltage in cn['length_by_voltages']:
                    if voltage in country_stat['length_by_voltages'].keys():
                        country_stat['length_by_voltages'][voltage][0] += cn['length_by_voltages'][voltage][0]
                        country_stat['length_by_voltages'][voltage][1] += cn['length_by_voltages'][voltage][1]
                        country_stat['length_by_voltages'][voltage][2] += cn['length_by_voltages'][voltage][2]
                        country_stat['length_by_voltages'][voltage][3] += cn['length_by_voltages'][voltage][3]
                    else:
                        country_stat['length_by_voltages'][voltage] = []
                        country_stat['length_by_voltages'][voltage].append(cn['length_by_voltages'][voltage][0])
                        country_stat['length_by_voltages'][voltage].append(cn['length_by_voltages'][voltage][1])
                        country_stat['length_by_voltages'][voltage].append(cn['length_by_voltages'][voltage][2])
                        country_stat['length_by_voltages'][voltage].append(cn['length_by_voltages'][voltage][3])

            countries_stats['aaa'] = country_stat

        return countries_stats
