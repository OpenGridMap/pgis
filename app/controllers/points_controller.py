from app.models.point import Point
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from geoalchemy2 import Geometry, func
from geoalchemy2.functions import GenericFunction
import app.helpers.point_form
from app import db

class PointsController:
    def index(self):
        if request.args.get('bounds') is None:
            return Response(json.dumps([]), mimetype='application/json')
        bounds_parts = request.args.get("bounds").split(',')
        points = Point.query.filter(func.ST_Contains(func.ST_MakeEnvelope(bounds_parts[1], bounds_parts[0], bounds_parts[3], bounds_parts[2]), Point.geom)).all()
#        points = Point.query.all()
        points = list(map(lambda point: point.serialize(), points))
        return Response(json.dumps(points),  mimetype='application/json')

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
