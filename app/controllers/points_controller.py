from app.models.point import Point
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from geoalchemy2 import Geometry, func
from geoalchemy2.functions import GenericFunction
import app.helpers.point_form
import base64
import sys
import os
from app import db
from sqlalchemy.sql import text

class PointsController:
    def index(self):
        if request.args.get('bounds') is None:
            return Response(json.dumps([]), mimetype='application/json')
        bounds_parts = request.args.get("bounds").split(',')
        points = Point.query.filter(func.ST_Contains(func.ST_MakeEnvelope(bounds_parts[1], bounds_parts[0], bounds_parts[3], bounds_parts[2]), Point.geom)).filter(Point.approved).all()
        points = list(map(lambda point: point.serialize(), points))
        return Response(json.dumps(points),  mimetype='application/json')

    def clustered(self):
        n_clusters = 5
        if request.args.get('bounds') is None:
            return Response(json.dumps([]), mimetype='application/json')
        bounds_parts = request.args.get("bounds").split(',')
        if request.args.get('zoom'):
            n_clusters = int(request.args.get('zoom'))
        #TODO this should be cached or precomputed
        query = text("SELECT kmeans, count(*), ST_X(ST_Centroid(ST_Collect(geom))), ST_Y(ST_Centroid(ST_Collect(geom))) AS geom FROM ( SELECT kmeans(ARRAY[ST_X(geom), ST_Y(geom)], :n_clusters) OVER (), geom FROM point WHERE ST_Contains(ST_MakeEnvelope(:bounds_1, :bounds_2, :bounds_3, :bounds_4), point.geom) AND point.approved = TRUE) AS ksub GROUP BY kmeans ORDER BY kmeans;")
        result = db.engine.execute(query, n_clusters=n_clusters, bounds_1=bounds_parts[1], bounds_2=bounds_parts[0], bounds_3=bounds_parts[3], bounds_4=bounds_parts[2])
        clusters = []
        for row in result:
             clusters.append({ 'count' : row[1], 'latlng': [float(row[2]), float(row[3])] })
        return Response(json.dumps(clusters),  mimetype='application/json')

    def edit(self, id):
        point = app.models.point.Point.query.get(id)
        form = app.helpers.point_form.PointForm(None, point) 
        form.properties.data = json.dumps(form.properties.data) if form.properties.data else ""
        return render_template('points/edit.html', form=form, point=point)
    
    def update(self, id):
        point = app.models.point.Point.query.get(id)
        form = app.helpers.point_form.PointForm(request.form, obj=point) 
        if form.validate_on_submit():
            form.populate_obj(point)
            db.session.add(point)
            db.session.commit()
            return redirect('/')
        return 'Error'

    def save_image(self,submission_id, encoded_string):
        directory = "app/uploads/submissions/" + submission_id 
        if not os.path.exists(directory):
            os.makedirs(directory)
        fh = open(directory + "/test.png", "wb")
        fh.write(base64.b64decode(encoded_string))
        fh.close()


