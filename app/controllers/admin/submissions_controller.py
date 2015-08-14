from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
from app.helpers.point_form import PointForm
from app.models.point import Point
from app.models.submission import Submission
from geoalchemy2 import Geometry, func
from flask.ext.login import current_user
from sqlalchemy.sql import text

class SubmissionsController:
    def index(self):
        page = int(request.args.get('page') or 1) 
        submissions = Submission.query.paginate(page, 20)
        return render_template('admin/submissions/index.html', submissions=submissions)

    def revise(self, id):
        form = PointForm() 
        submission = Submission.query.get(id)
        query = text("SELECT ST_X(ST_CENTROID(ST_COLLECT(geom))), ST_Y(ST_CENTROID(ST_COLLECT(geom))) FROM point WHERE submission_id=:submission_id")
        mid_point = list(db.engine.execute(query, submission_id=32).first())
        return render_template('admin/submissions/revise.html', submission=submission, form=form, mid_point=mid_point)

    def merge(self, id):
        pass

    def delete(self, id):
        point = Point.query.get(id)
        db.session.delete(point)
        db.session.commit()
        return redirect(url_for('admin_points'))
