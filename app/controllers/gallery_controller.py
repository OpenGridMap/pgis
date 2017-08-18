import os

from flask import render_template, json, Response, \
    send_from_directory
from flask_resize import generate_image
from sqlalchemy.orm import contains_eager

from app import db
from app.models.point import Point
from app.models.submission import Submission


class GalleryController:
    def index(self):
        return render_template('gallery.html', title='Submissions Gallery')

    def data(self):
        submissions = db.session.query(Submission). \
            join(Submission.points).outerjoin(Point.pictures_for_gallery).join(Submission.user). \
            options(contains_eager(Submission.points).contains_eager(Point.pictures_for_gallery)). \
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
