from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.point_form
import app.models.point

class PointsController:
    def index(self):
        points = app.models.point.Point.query.all()
        return render_template('admin/points/index.html', points=points)

    def new(self):
        form = app.helpers.point_form.PointForm() 
        return render_template('admin/points/new.html', form=form)

    def create(self):
        form = app.helpers.point_form.PointForm() 
        if form.validate_on_submit():
            geometry = "POINT({} {})".format(form.latitude.data, form.longitude.data)
            new_point = app.models.point.Point(name=form.name.data, geom=geometry)
            db.session.add(new_point)
            db.session.commit()
            return redirect(url_for('admin_points'))
        return 'Error'

    def delete(self, id):
        point = app.models.point.Point.query.get(id)
        db.session.delete(point)
        db.session.commit()
        return redirect(url_for('admin_points'))
