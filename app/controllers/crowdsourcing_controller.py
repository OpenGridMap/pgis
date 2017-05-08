from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
from app.models.crowdsourcing_polygon import CrowdsourcingPolygon
from geoalchemy2.functions import GenericFunction
from geoalchemy2 import Geometry, func
from app.models.point import Point
from geoalchemy2.shape import to_shape

class CrowdsourcingController:
    # highest point score, one polygon has
    numPoints = 0
    # polygon with the most points inside
    winnerPolygons = []

    def index(self):
        polygons = db.session.query(CrowdsourcingPolygon.id, CrowdsourcingPolygon.geom, func.count(Point.geom).label("num_points")).outerjoin(Point, func.ST_Contains(CrowdsourcingPolygon.geom, Point.geom)).group_by(CrowdsourcingPolygon.id)

        #map(self.mostPoints, polygons)
        for polygon in polygons:
            self.mostPoints(polygon)

        polygons = map(lambda polygon: {'id': polygon.id, 'geom': list(to_shape(polygon.geom).exterior.coords),
                                        'num_points': polygon.num_points, 'is_winner': self.is_winner(polygon.id)}, polygons)
        polygons = list(polygons)
        return Response(json.dumps(polygons), mimetype='application/json')

    def mostPoints(self, polygon):
        if polygon.num_points > self.numPoints:
            self.numPoints = polygon.num_points
            self.winnerPolygons = [polygon.id]
        elif polygon.num_points == self.numPoints:
            self.winnerPolygons.append(polygon.id)
        return polygon

    def is_winner(self, polygon_id):
        return polygon_id in self.winnerPolygons