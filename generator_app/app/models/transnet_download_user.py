from datetime import datetime

from app import db


class TransnetDownloadUser(db.Model):
    __tablename__ = 'transnet_download_user'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    organization = db.Column(db.String, nullable=False)
    purpose = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    url = db.Column(db.String, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    logs = db.relationship('TransnetDownloadLog', back_populates='download_user')

    @staticmethod
    def create_user(form):
        if form.validate():
            new_user = TransnetDownloadUser()
            form.populate_obj(new_user)
            db.session.add(new_user)
            db.session.commit()
            return new_user.uuid
