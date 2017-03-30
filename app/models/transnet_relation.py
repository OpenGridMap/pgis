from geoalchemy2 import Geography
from geoalchemy2 import func
from sqlalchemy import cast
from sqlalchemy.orm import joinedload

from app import db
from app.models.transnet_country import TransnetCountry
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
            powerlines_qry = powerlines_qry.filter(
                TransnetPowerline.relations.any(TransnetRelation.voltage.in_(voltages)))

        powerline_relations = powerlines_qry.options(joinedload('relations')).all()

        return TransnetRelation.prepare_relations_for_export(powerline_relations, [], zoom, voltages)

    @staticmethod
    def relations_for_export(relation_ids):

        relations = TransnetRelation.query.filter(
            TransnetRelation.id.in_(relation_ids)
        ).all()

        return TransnetRelation.prepare_relations_for_export([], relations, None, None)

    @staticmethod
    def get_station_info(relation_id):

        relations = TransnetRelation.query.filter(
            TransnetRelation.id == relation_id
        ).all()

        return TransnetRelation.prepare_relations_for_export([], relations, None, None)

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
    def prepare_relations_for_export(powerline_relations, relations_filtered, zoom, voltages):

        relations_to_export = {}

        relations_query = set()

        relations_query.update(relations_filtered)
        [relations_query.update([r for r in x.relations]) for x in powerline_relations]

        for relation in relations_query:
            for powerline in relation.powerlines:
                # if (not voltages or  any(v in powerline.voltage for v in voltages)) and powerline.length > 10000:
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
        station_tags = ['substation', 'station', 'sub_station']
        plant_tags = ['plant', 'generator']

        countries_stats = {}
        for country in countries:

            country_stat = {
                'all_line_length_with_duplicates': 0,
                'plants_count': 0,
                'substations_count': 0,
                'length_by_voltages': {},
                'relation_length_by_voltages': {}
            }
            try:

                country_stat['all_line_length_with_duplicates'] = \
                    db.session.query(func.sum(TransnetPowerline.length * TransnetPowerline.osm_replication).label(
                        'sum_line')).filter(
                        TransnetPowerline.country == country)[0][0] / 1000

                country_stat['plants_count'] = db.session.query(func.count(TransnetStation.id)).filter(
                    TransnetStation.country == country).filter(
                    TransnetStation.type.in_(plant_tags))[0][0]

                country_stat['substations_count'] = db.session.query(func.count(TransnetStation.id)).filter(
                    TransnetStation.country == country).filter(
                    TransnetStation.type.in_(station_tags))[0][0]

                voltages = db.session.query(func.unnest(TransnetPowerline.voltage)).filter(
                    TransnetPowerline.country == country).distinct()

                relations_voltages = db.session.query(func.unnest(TransnetCountry.voltages)).filter(
                    TransnetCountry.country == country).distinct()

                for voltage in relations_voltages:
                    country_stat['relation_length_by_voltages'][voltage[0]] = 0

                    length_with_dup = db.session \
                        .query(func.sum(TransnetPowerline.length * TransnetPowerline.osm_replication).label('sum_line')) \
                        .filter(TransnetPowerline.country == country) \
                        .filter(TransnetPowerline.voltage.any(voltage)) \
                        .filter(TransnetPowerline.relations.any(TransnetRelation.voltage.in_([voltage])))

                    if length_with_dup.count() and length_with_dup[0][0]:
                        country_stat['relation_length_by_voltages'][voltage[0]] = length_with_dup[0][0] / 1000

                for voltage in voltages:
                    country_stat['length_by_voltages'][voltage[0]] = 0

                    length_shared_with_dup = db.session.query(
                        func.sum(TransnetPowerline.length * TransnetPowerline.osm_replication).label(
                            'sum_line')).filter(
                        TransnetPowerline.country == country).filter(TransnetPowerline.voltage.any(voltage[0]))
                    if length_shared_with_dup.count() and length_shared_with_dup[0][0]:
                        country_stat['length_by_voltages'][voltage[0]] = length_shared_with_dup[0][0] / 1000

            except Exception as ex:
                print(ex)
            countries_stats[country] = country_stat

        if len(countries) > 1:
            country_stat = {
                'all_line_length_with_duplicates': sum(
                    [cn['all_line_length_with_duplicates'] for cn in countries_stats.values()]),
                'plants_count': sum([cn['plants_count'] for cn in countries_stats.values()]),
                'substations_count': sum([cn['substations_count'] for cn in countries_stats.values()]),
                'length_by_voltages': {},
                'relation_length_by_voltages': {}
            }
            for cn in countries_stats.values():
                for voltage in cn['length_by_voltages'].keys():
                    if voltage in country_stat['length_by_voltages'].keys():
                        country_stat['length_by_voltages'][voltage] += cn['length_by_voltages'][voltage]
                    else:
                        country_stat['length_by_voltages'][voltage] = cn['length_by_voltages'][voltage]
            for cn in countries_stats.values():
                for voltage in cn['relation_length_by_voltages'].keys():
                    if voltage in country_stat['relation_length_by_voltages'].keys():
                        country_stat['relation_length_by_voltages'][voltage] += \
                            cn['relation_length_by_voltages'][voltage]
                    else:
                        country_stat['relation_length_by_voltages'][voltage] = cn['relation_length_by_voltages'][voltage]

            countries_stats['aaa'] = country_stat

        return countries_stats
