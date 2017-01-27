from datetime import datetime

from app import db
from app.models.transnet_download_user import TransnetDownloadUser


class TransnetDownloadLog(db.Model):
    __tablename__ = 'transnet_download_log'
    id = db.Column(db.Integer, primary_key=True)
    bounds = db.Column(db.String, nullable=True)
    countries = db.Column(db.String, nullable=True)
    voltages = db.Column(db.String, nullable=True)
    relations_ids = db.Column(db.String, nullable=True)
    type = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    download_user = db.relationship('TransnetDownloadUser', back_populates='logs')
    download_user_id = db.Column(db.Integer, db.ForeignKey('transnet_download_user.id', ondelete='CASCADE'),
                                 nullable=True, )

    @staticmethod
    def add_log(uuid, file_type, bounds=None, countries=None, voltages=None, relations_ids=None):
        user_id = db.session.query(TransnetDownloadUser.id).filter_by(uuid=uuid).scalar()
        if user_id:
            new_log = TransnetDownloadLog()
            new_log.bounds = bounds
            new_log.relations_ids = relations_ids
            new_log.countries = countries
            new_log.voltages = voltages
            new_log.type = file_type
            new_log.download_user_id = user_id
            db.session.add(new_log)
            db.session.commit()
            return uuid
