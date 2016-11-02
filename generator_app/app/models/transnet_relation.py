from geoalchemy2 import Geography
from geoalchemy2 import func
from shapely.geometry import MultiPoint
from sqlalchemy import cast
from sqlalchemy.orm import joinedload

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
        TransnetStation.query.all()

    @staticmethod
    def with_points_and_lines_in_bounds(bounds, voltages, countries):

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

        return TransnetRelation.prepare_relations_for_export(powerline_relations, [])

    @staticmethod
    def relations_for_export(relation_ids):

        relations = TransnetRelation.query.filter(
            TransnetRelation.id.in_(relation_ids)
        ).all()

        return TransnetRelation.prepare_relations_for_export([], relations)

    @staticmethod
    def prepare_relations_for_export(powerline_relations, relations_filtered, ):

        relations_query = set()

        relations_query.update(relations_filtered)
        [relations_query.update([r for r in x.relations]) for x in powerline_relations]

        component_points_points = []

        for relation in relations_query:
            for powerline in relation.powerlines:
                component_points_points.extend([(x, y) for x, y in powerline.shape().coords])
            for station in relation.stations:
                component_points_points.extend(station.shape().exterior.coords)

        equipments_multipoint = MultiPoint(component_points_points)
        map_centroid = equipments_multipoint.centroid

        return relations_query, map_centroid
