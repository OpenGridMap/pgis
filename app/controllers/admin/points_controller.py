from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.point_form
from app.models.point import Point
from app.models.submission import Submission
from app.models.picture import Picture
from osmapi import OsmApiError

class PointsController:
    def index(self):
        page = int(request.args.get('page') or 1)
        points = Point.query.filter(Point.approved).paginate(page, 20)
        return render_template('admin/points/index.html', points=points)

    def new(self):
        form = app.helpers.point_form.PointForm()
        if request.args.get("redirect_back"):
            session["redirect_back"] = True
        return render_template('admin/points/new.html', form=form)

    def create(self):
        form = app.helpers.point_form.PointForm()
        if form.validate_on_submit():
            new_point = Point()
            form.populate_obj(new_point)
            db.session.add(new_point)
            db.session.commit()
            try:
                new_point.postToOSM()
            except OsmApiError as e:
                print("Exception while trying OSM Api call")
                print(e)
            if "redirect_back" in session:
                del session["redirect_back"]
                return redirect(url_for('index', lat=new_point.shape().x, long=new_point.shape().y,  zoom=18))
            else:
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
            try:
                point.updateOnOSM()
            except OsmApiError as e:
                print("Exception while trying OSM Api call")
                print(e)

            if "redirect_back" in session:
                del session["redirect_back"]
                return redirect(url_for('index', lat=point.shape().x, long=point.shape().y,  zoom=18))
            else:
                return redirect(url_for('admin_points'))

        return 'Error'

    def delete(self, id):
        point = Point.query.get(id)
        try:
            point.deleteOnOSM()
        except OsmApiError as e:
            print("Exception while trying OSM Api call")
            print(e)
        db.session.query(Picture).filter(Picture.point_id == point.id).delete()
        db.session.delete(point)
        if point.submission_id is not None:
            submission = Submission.query.get(point.submission_id)
            if submission is not None and db.session.query(Point).filter(Point.submission_id == submission.id).count == 0:
                db.session.query(Submission).filter(Submission.id == point.submission_id).delete()
        db.session.commit()
        return redirect(url_for('admin_points'))
