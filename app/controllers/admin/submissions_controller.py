from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.point_form
from app.models.point import Point

class SubmissionsController:
    def index(self):
        page = int(request.args.get('page') or 1) 
        points = Point.query.filter(Point.revised == False).paginate(page, 20)
        return render_template('admin/points/index.html', points=points)

    def delete(self, id):
        point = Point.query.get(id)
        db.session.delete(point)
        db.session.commit()
        return redirect(url_for('admin_points'))
