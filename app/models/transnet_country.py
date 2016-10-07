from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ARRAY

from app import db


class TransnetCountry(db.Model):
    __tablename__ = 'transnet_country'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    continent = db.Column(db.String)
    voltages = db.Column(ARRAY(db.INTEGER), nullable=True)

    @staticmethod
    def get_countries():
        continents = db.session.query(TransnetCountry.continent).distinct()

        world = {}
        for continent in continents:
            world[continent[0]] = TransnetCountry.query.filter(TransnetCountry.continent == continent[0]).order_by(
                TransnetCountry.country).all()

        return world

    @staticmethod
    def get_voltages():
        voltages = db.session.query(func.unnest(TransnetCountry.voltages)).distinct()
        return sorted([x[0] for x in voltages])
