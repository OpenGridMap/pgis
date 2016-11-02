from app import db


class TransnetRelationStation(db.Model):
    __tablename__ = 'transnet_relation_station'
    relation_id = db.Column('relation_id', db.Integer, db.ForeignKey('transnet_relation.id'),
                            nullable=False, primary_key=True)
    station_id = db.Column('station_id', db.Integer, db.ForeignKey('transnet_station.id'),
                           nullable=False, primary_key=True)
    db.Column('country', db.String, nullable=False)
