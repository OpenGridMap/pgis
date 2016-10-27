from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import ARRAY

from app import db


class ScigridPowerline(db.Model):
    __tablename__ = 'scigrid_powerline'
    id = db.Column(db.Integer, primary_key=True)
    l_id = db.Column(db.Integer, nullable=True)
    v_id_1 = db.Column(db.Integer, nullable=True)
    v_id_2 = db.Column(db.Integer, nullable=True)
    voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    cables = db.Column(ARRAY(db.INTEGER), nullable=True)
    wires = db.Column(ARRAY(db.INTEGER), nullable=True)
    frequency = db.Column(ARRAY(db.INTEGER), nullable=True)
    name = db.Column(db.String, nullable=True)
    operator = db.Column(db.String, nullable=True)
    ref = db.Column(db.String, nullable=True)
    length_m = db.Column(db.NUMERIC, nullable=True)
    r_ohmkm = db.Column(db.NUMERIC, nullable=True)
    x_ohmkm = db.Column(db.NUMERIC, nullable=True)
    c_nfkm = db.Column(db.NUMERIC, nullable=True)
    i_th_max_a = db.Column(db.NUMERIC, nullable=True)
    from_relation = db.Column(db.BOOLEAN, nullable=True)
    geom = db.Column(Geometry('LINESTRING'), nullable=True)
    geom_str = db.Column(db.String, nullable=True)

    def shape(self):
        return to_shape(self.geom)


class ScigridStation(db.Model):
    __tablename__ = 'scigrid_station'
    id = db.Column(db.Integer, primary_key=True)
    v_id = db.Column(db.Integer, nullable=True)
    lon = db.Column(db.NUMERIC, nullable=True)
    lat = db.Column(db.NUMERIC, nullable=True)
    type = db.Column(db.String, nullable=True)
    voltage = db.Column(ARRAY(db.INTEGER), nullable=True)
    frequency = db.Column(ARRAY(db.INTEGER), nullable=True)
    name = db.Column(db.String, nullable=True)
    operator = db.Column(db.String, nullable=True)
    ref = db.Column(db.String, nullable=True)
    geom = db.Column(Geometry('POINT'), nullable=True)
    geom_str = db.Column(db.String, nullable=True)

    def shape(self):
        return to_shape(self.geom)
