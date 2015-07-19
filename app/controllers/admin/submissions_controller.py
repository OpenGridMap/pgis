from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.point_form
from app.models.point import Point
from geoalchemy2 import Geometry, func

class SubmissionsController:
    def index(self):
        page = int(request.args.get('page') or 1) 
        submissions = Point.query.with_entities(Point.submission_id, func.count(Point.id).label("count_points")).filter(Point.revised == False).group_by(Point.submission_id).paginate(page, 20)
        return render_template('admin/submissions/index.html', submissions=submissions)

    def delete(self, id):
        point = Point.query.get(id)
        db.session.delete(point)
        db.session.commit()
        return redirect(url_for('admin_points'))
