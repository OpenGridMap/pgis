from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
from app.models.crowdsourcing_polygon import CrowdsourcingPolygon
from geoalchemy2.functions import GenericFunction
from geoalchemy2 import Geometry, func
from app.models.point import Point
from geoalchemy2.shape import to_shape

class CrowdsourcingController:

    def index(self):
        polygons = db.session.query(CrowdsourcingPolygon.id, CrowdsourcingPolygon.geom, func.count(Point.geom).label("num_points")).outerjoin(Point, func.ST_Contains(CrowdsourcingPolygon.geom, Point.geom)).group_by(CrowdsourcingPolygon.id)

        polygons = map(lambda polygon: {'id': polygon.id, 'geom': list(to_shape(polygon.geom).exterior.coords), 'num_points': polygon.num_points}, polygons)
        polygons = list(polygons)
        return Response(json.dumps(polygons), mimetype='application/json')