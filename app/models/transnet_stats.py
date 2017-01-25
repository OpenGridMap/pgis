from sqlalchemy import func

from app import db


class TransnetStats(db.Model):
    __tablename__ = 'transnet_stats'
    id = db.Column(db.Integer, primary_key=True)
    last_updated = db.Column(db.Date)

    @staticmethod
    def get_last_updated():
        return db.session.query(func.max(TransnetStats.last_updated))
