from app.models.point import Point
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response

class PointsController:
	def index(self):
		points = list(map(lambda point: point.serialize(), Point.query.all()))
		return Response(json.dumps(points),  mimetype='application/json')