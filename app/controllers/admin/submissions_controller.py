from app import GisApp
import sys, os, traceback, base64, shutil
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
from app.helpers.point_form import PointForm
from app.models.point import Point
from app.models.submission import Submission
from app.models.user import User
from app.models.picture import Picture
from geoalchemy2 import Geometry, func
from flask.ext.login import current_user
from sqlalchemy.sql import text
from sqlalchemy import and_
from enum import Enum
GisApp.config['RESIZE_URL'] = 'http://vmjacobsen39.informatik.tu-muenchen.de/static/uploads'
GisApp.config['RESIZE_ROOT'] = 'app/static/uploads/'
import flask_resize

# Predefined activity points
class Activity(Enum):
    new_transformer = 0
    existing_transformer = 0
    new_other_point = 0
    existing_other_point = 0
    revise_submission = 0 # revise submission not implemented at moment

class SubmissionsController:
    def index(self):
        page = int(request.args.get('page') or 1)
        submission_filter = int(request.args.get('filter') or 1)
        # revised true, approved false
        if (submission_filter == 2):
            submissions = Submission.query.filter(Submission.revised == True, Submission.approved == False).order_by(Submission.id).paginate(page, 20)
        # revised true, approved true
        elif(submission_filter == 3):
            submissions = Submission.query.filter(Submission.revised == True, Submission.approved == True).order_by(Submission.id).paginate(page, 20)
        # revised false, approved false
        else:
            submissions = Submission.query.filter(Submission.revised == False).order_by(Submission.id).paginate(page, 20)
        return render_template('admin/submissions/index.html', submissions=submissions, submission_filter=submission_filter)

    def revise(self, id):
        flask_resize.Resize(GisApp)
        #form = PointForm()
        submission = Submission.query.get(id)
        submission_merged = False
        try:
            point = db.session.query(Point).filter(Point.submission_id == id).one()
            if (point.merged_to != None):
                submission_merged = True;
        except:
            point = db.session.query(Point).filter(Point.submission_id == id, Point.merged_to == None).one()
            submission_merged = True

        form = PointForm(None, point)
        form.properties.data = json.dumps(form.properties.data) if form.properties.data else ""
        query = text("SELECT ST_X(ST_CENTROID(ST_COLLECT(geom))), ST_Y(ST_CENTROID(ST_COLLECT(geom))) FROM point WHERE submission_id=:submission_id")
        mid_point = list(db.engine.execute(query, submission_id=id).first())
        return render_template('admin/submissions/revise.html', submission=submission, form=form, point=point, mid_point=mid_point, submission_merged=submission_merged)

    def accept_submission(self, id):
        form = PointForm()
        if form.validate_on_submit():
            point = db.session.query(Point).filter(Point.submission_id == id).first()
            form.populate_obj(point)
            db.session.add(point)
            db.session.query(Submission).filter(Submission.id == id)\
                .update({Submission.revised: True, Submission.approved: True}, synchronize_session=False)

            # add activity points for submitter
            user_id = db.session.query(Submission.user_id).filter(Submission.id == id).subquery()
            power_element_tags = point.properties.get('tags', {}).get('power_element_tags', None)
            if 'power=transformer' in power_element_tags:
                activityPoints = Activity.new_transformer.value
            else:
                activityPoints = Activity.new_other_point.value
            db.session.query(User).filter(User.id == user_id)\
                .update({User.activity_points: User.activity_points + activityPoints,
                         User.activity_points_total: User.activity_points_total + activityPoints},
                        synchronize_session=False)

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

    def reject_submission(self, id):
        db.session.query(Submission).filter(Submission.id == id)\
            .update({Submission.revised: True,Submission.approved: False}, synchronize_session=False)
        db.session.query(Point).filter(Point.submission_id == id).update({Point.revised: True, Point.approved: False},
                                                                         synchronize_session=False)
        db.session.commit()
        submission = db.session.query(Submission).filter(Submission.revised == False).first()
        return redirect(url_for('submissions_index'))

    def merge(self, id):
        form = PointForm()
        if form.validate_on_submit():

            # original point before merging process, submitted by app
            submitted_point = db.session.query(Point).filter(Point.submission_id == id).one()

            new_point = Point()
            form.populate_obj((new_point))
            new_point.submission_id = id
            db.session.add(new_point)
            db.session.commit()

            # get old point because submission_id is needed for copying pictures if there is a submission_id
            old_point = Point.query.get(form.merge_with.data)


            # set merged_to in old point and set the visibility to false
            db.session.query(Point).filter(Point.id == form.merge_with.data)\
                .update({Point.merged_to: new_point.id, Point.approved: False}, synchronize_session=False)

            submitted_point.revised = True
            submitted_point.merged_to = new_point.id
            submitted_point.approved = False # set approved to False, also if the point was approved already
            db.session.add(submitted_point)

            #db.session.query(Picture)\
            #    .filter(or_(Picture.point_id == submitted_point, Picture.point_id == form.merge_with.data))\
            #    .update({Picture.point_id: new_point.id}, synchronize_session=False)
            db.session.query(Submission).filter(Submission.id == id)\
                .update({Submission.revised: True, Submission.approved: True}, synchronize_session=False)
            user_id = db.session.query(Submission.user_id).filter(Submission.id == id).subquery()

            # Add activity points for submitter
            power_element_tags = new_point.properties.get('tags', {}).get('power_element_tags', None)

            # if old point not submitted by app (= no picture exists)
            if old_point.submission_id == None:
                if 'power=transformer' in power_element_tags:
                    activityPoints = Activity.new_transformer.value
                else:
                    activityPoints = Activity.new_other_point.value

            else:
                if 'power=transformer' in power_element_tags:
                    activityPoints = Activity.existing_transformer.value
                else:
                    activityPoints = Activity.existing_other_point.value
            db.session.query(User).filter(User.id == user_id) \
                .update({User.activity_points: User.activity_points + activityPoints,
                         User.activity_points_total: User.activity_points_total + activityPoints},
                        synchronize_session=False)

            db.session.commit()
            # copy the necessary rows in picture table and adapt them
            #query = text("INSERT INTO picture ( point_id, submission_id, user_id, filepath) SELECT :new_point_id, "
            #":new_point_submission_id, user_id, "
            #"'static/uploads/submissions/' || :new_point_submission_id || '/' || point_id || '.jpg' "
            #"FROM picture WHERE point_id = :submitted_point_id or point_id = :old_point_id;")
            #db.engine.execute(query, new_point_id=new_point.id, new_point_submission_id=new_point.submission_id, submitted_point_id=submitted_point.id, old_point_id=form.merge_with.data)

            #picture = Picture()
            #picture.point_id = new_point.id
            #picture.submission_id = new_point.submission_id
            #picture.filepath = 'static/uploads/submissions/' + str(new_point.submission_id) + '/' + str(new_point.id) + '.jpg'
            #picture.user_id = new_point.submission.user_id
            #db.session.add(picture)

            #changed, because point_id of pictures of a merged point should be the same
            #all_points = db.session.query(Point).filter(and_(Point.merged_to == new_point.id, Point.submission_id != new_point.submission_id)).all()
            all_points = db.session.query(Point).filter(Point.merged_to == new_point.id).all()
            for next_point in all_points:
                picture = Picture()
                picture.point_id = new_point.id
                picture.submission_id = new_point.submission_id
                picture.filepath = 'static/uploads/submissions/' + str(new_point.submission_id) + '/' + str(next_point.id) + '.jpg'
                picture.user_id = next_point.submission.user_id
                db.session.add(picture)
            db.session.commit()

            self.__merge_photos(old_point.submission_id, new_point.submission_id)
            return redirect(url_for('submissions_index'))
        return 'Error'

    def delete(self, id):
        submission = Submission.query.get(id)
        shutil.rmtree("app/static/uploads/submissions/" + str(submission.id), ignore_errors=True)
        db.session.query(Point).filter(Point.submission_id == id).delete()
        db.session.delete(submission)
        db.session.commit()
        return redirect(url_for('submissions_index'))

    # copying pictures from merged point to new point
    def __merge_photos(self, source_submission, destination_submission):
        dest = "app/static/uploads/submissions/" + str(destination_submission)
        if not os.path.exists(dest):
            os.makedirs(dest)
        # copy pictures from old point
        src_dir = "app/static/uploads/submissions/" + str(source_submission)
        try:
            src_files = os.listdir(src_dir)
            for file_name in src_files:
                full_file_name = os.path.join(src_dir, file_name)
                if (os.path.isfile(full_file_name)):
                    shutil.copy(full_file_name, dest)
        # points imported from OpenStreetMap have no pictures. This points throw a FileNotFoundError
        except FileNotFoundError:
            pass


