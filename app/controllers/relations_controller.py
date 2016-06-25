from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from geoalchemy2 import Geometry, func
from geoalchemy2.functions import GenericFunction
import app.helpers.point_form
import base64
import sys
import os
from app import db
from sqlalchemy.sql import text

class RelationsController:
    def index(self):
        if request.args.get('bounds') is None:
            return Response(json.dumps([]), mimetype='application/json')
        bounds_parts = request.args.get("bounds").split(',')
        # points = Point.query.filter(
        #     func.ST_Contains(func.ST_MakeEnvelope(bounds_parts[1], bounds_parts[0], bounds_parts[3], bounds_parts[2]), Point.geom)).filter(Point.approved).all()
        # points = list(map(lambda point: point.serialize(), points))
        # return Response(json.dumps(points),  mimetype='application/json')



        bounds_parts = ['12.007412910461426', '50.12731909362077', '12.062344551086424', '50.14627133560579']
        # Query to get the points and nodes that are part of a relation that
        # has points that are in the bounds
        relation_and_point_ids_query = text("""
            SELECT DISTINCT p2.id, r.id FROM point p
            JOIN power_relation_members m
                ON p.id = m.member_id
            JOIN power_relation_members m2
                ON m2.power_relation_id = m.power_relation_id
            JOIN point p2
                ON p2.id = m2.member_id
            JOIN power_relations r
                ON r.id = m.power_relation_id
            WHERE ST_Contains(
                ST_MakeEnvelope(:bounds_1, :bounds_2, :bounds_3, :bounds_4),
                p.geom
            )
         """)

        relation_and_point_ids = db.engine.execute(
            relation_and_point_ids_query,
            bounds_1=bounds_parts[1],
            bounds_2=bounds_parts[0],
            bounds_3=bounds_parts[3],
            bounds_4=bounds_parts[2]
        )

        points = []
        for row in relation_and_point_ids:
            points.append({ 'id': row[0], 'relation_id': row[1] })

        return Response(json.dumps(points), mimetype='application/json')
