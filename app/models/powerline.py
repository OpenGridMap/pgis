from app import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

class Powerline(db.Model):
	id 	 = db.Column(db.Integer, primary_key=True)
	geom = db.Column(Geometry('LINESTRING'))
