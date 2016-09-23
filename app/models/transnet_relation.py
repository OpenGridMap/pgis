from sqlalchemy.dialects.postgresql import ARRAY

from app import db


class TransnetRelation(db.Model):
    __tablename__ = 'transnet_relation'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    ref = db.Column(db.String, nullable=True)

    def serialize(self):
        return {"id": self.id, }
