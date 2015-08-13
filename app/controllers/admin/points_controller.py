from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.point_form
from app.models.point import Point

class PointsController:
    def index(self):
        page = int(request.args.get('page') or 1) 
        points = Point.query.filter(Point.revised).paginate(page, 20)
        return render_template('admin/points/index.html', points=points)

    def new(self):
        form = app.helpers.point_form.PointForm() 
        return render_template('admin/points/new.html', form=form)

    def create(self):
        form = app.helpers.point_form.PointForm() 
        if form.validate_on_submit():
            new_point = Point()
            form.populate_obj(new_point)
            db.session.add(new_point)
            db.session.commit()
            return redirect(url_for('admin_points'))
        return 'Error'
    
    def edit(self, id):
        point = Point.query.get(id)
        form = app.helpers.point_form.PointForm(None, point) 
        form.properties.data = json.dumps(form.properties.data) if form.properties.data else ""
        if request.args.get("redirect_back"):
            session["redirect_back"] = True
        return render_template('admin/points/edit.html', form=form, point=point)
    
    def update(self, id):
        point = Point.query.get(id)
        form = app.helpers.point_form.PointForm(request.form, obj=point) 
        if form.validate_on_submit():
            form.populate_obj(point)
            db.session.add(point)
            db.session.commit()
            if "redirect_back" in session:
                del session["redirect_back"]
                return redirect(url_for('index', lat=point.shape().x, long=point.shape().y,  zoom=18))
            else:
                return redirect(url_for('admin_points'))

        return 'Error'

    def delete(self, id):
        point = Point.query.get(id)
        db.session.delete(point)
        db.session.commit()
        return redirect(url_for('admin_points'))
