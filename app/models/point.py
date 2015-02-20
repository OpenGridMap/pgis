from app import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

class Point(db.Model):
	id 	 = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	geom = db.Column(Geometry('POINT'))

	def serialize(self):
		point = self.shape()
		return [point.x, point.y]
	
	def shape(self):
		return to_shape(self.geom)