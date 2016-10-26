from app import db


class TransnetRelationPowerline(db.Model):
    __tablename__ = 'transnet_relation_powerline'
    relation_id = db.Column('relation_id', db.Integer, db.ForeignKey('transnet_relation.id'),
                            nullable=False, primary_key=True)
    powerline_id = db.Column('powerline_id', db.Integer, db.ForeignKey('transnet_powerline.id'),
                             nullable=False, primary_key=True)
    db.Column('country', db.String, nullable=False)
