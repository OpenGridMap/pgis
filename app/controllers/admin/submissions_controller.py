from app import GisApp
import sys, os, traceback, base64, shutil
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
from app.helpers.point_form import PointForm
from app.models.point import Point
from app.models.submission import Submission
from geoalchemy2 import Geometry, func
from flask.ext.login import current_user
from sqlalchemy.sql import text
GisApp.config['RESIZE_URL'] = 'http://vmjacobsen39.informatik.tu-muenchen.de/static/uploads'
GisApp.config['RESIZE_ROOT'] = 'app/static/uploads/'
import flask_resize

class SubmissionsController:
    def index(self):
        page = int(request.args.get('page') or 1)
        submissions = Submission.query.filter(Submission.revised == False).order_by(Submission.id).paginate(page, 20)
        return render_template('admin/submissions/index.html', submissions=submissions)

    def revise(self, id):
        flask_resize.Resize(GisApp)
        #form = PointForm()
        submission = Submission.query.get(id)
        point = db.session.query(Point).filter(Point.submission_id == id).first()
        form = PointForm(None, point)
        form.properties.data = json.dumps(form.properties.data) if form.properties.data else ""
        query = text("SELECT ST_X(ST_CENTROID(ST_COLLECT(geom))), ST_Y(ST_CENTROID(ST_COLLECT(geom))) FROM point WHERE submission_id=:submission_id")
        mid_point = list(db.engine.execute(query, submission_id=id).first())
        return render_template('admin/submissions/revise.html', submission=submission, form=form, mid_point=mid_point)

    def accept_submission(self, id):
        form = PointForm()
        if form.validate_on_submit():
            point = db.session.query(Point).filter(Point.submission_id == id).first()
            form.populate_obj(point)
            db.session.add(point)
            db.session.query(Submission).filter(Submission.id == id).update({Submission.revised: True}, synchronize_session=False)
            db.session.commit()
            if request.form.get('btn') == 'accept_go_next':
                submission = db.session.query(Submission).filter(Submission.revised == False).first()
                if submission is not None:
                    return redirect(url_for('submissions_revise', id=submission.id))
                else:
                    return redirect(url_for('submissions_index'))
            else:
                return redirect(url_for('submissions_index'))
        return 'Error'

    def merge_new(self, id): # working, but not used at the moment
        form = PointForm()
        if form.validate_on_submit():
            new_point = Point()
            form.populate_obj(new_point)
            new_point.submission_id = id
            db.session.add(new_point)
            db.session.query(Submission).filter(Submission.id == id).update({Submission.revised: True}, synchronize_session=False)
            db.session.commit()
            self.__merge_photos(id, new_point.id)
            return redirect(url_for('submissions_index'))
        return 'Error'

    def merge_existing(self, id):
        pass

    def delete(self, id):
        submission = Submission.query.get(id)
        shutil.rmtree("app/static/uploads/submissions/" + str(submission.id), ignore_errors=True)
        db.session.query(Point).filter(Point.submission_id == id).delete()
        db.session.delete(submission)
        db.session.commit()
        return redirect(url_for('submissions_index'))

    def __merge_photos(self, submission_id, point_id):
        dest = "app/static/uploads/points/" + str(point_id)
        if not os.path.exists(dest):
            os.makedirs(dest)

        src_dir = "app/static/uploads/submissions/" + str(submission_id)
        src_files = os.listdir(src_dir)
        for file_name in src_files:
            full_file_name = os.path.join(src_dir, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dest)
