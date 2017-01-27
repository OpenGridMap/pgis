from app import GisApp
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response, \
    send_from_directory, send_file
from geoalchemy2 import Geometry, func
from geoalchemy2.functions import GenericFunction
import app.helpers.point_form
import sys, os, traceback, base64
import hashlib
from app import db
from app.models.point import Point
from app.models.submission import Submission
from app.models.picture import Picture
from app.models.user import User
from flask.ext.login import current_user
from httplib2 import Http
from flask.ext.hashing import Hashing
from sqlalchemy.orm import contains_eager
from random import randint, uniform
from shutil import copy2
from flask_resize import generate_image


class GalleryController:
    def index(self):
        return render_template('gallery.html', title='Submissions Gallery')

    def data(self):
        submissions = db.session.query(Submission). \
            join(Submission.points).outerjoin(Point.pictures). \
            options(contains_eager(Submission.points).contains_eager(Point.pictures)). \
            all()

        submissions = list(map(lambda submission: submission.serialize_for_gallery(), submissions))

        return Response(json.dumps(submissions), mimetype='application/json')

    def thumb(self, path, height=50):
        submission_id, img_filename = path.split('/')[-2:]
        thumb_filename = '%d_%s_%s' % (height, submission_id, img_filename)

        img_path = os.path.join('app', 'static', 'uploads', 'submissions', submission_id, img_filename)
        thumb_path = os.path.join('app', 'static', 'uploads', 'cache', thumb_filename)

        if not os.path.exists(thumb_path):
            generate_image(img_path, thumb_path, height=height, progressive=True)

        thumb_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads', 'cache')

        return send_from_directory(directory=thumb_dir, filename=thumb_filename, mimetype='image/jpg',
                                   as_attachment=False)
