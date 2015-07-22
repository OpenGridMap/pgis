from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from geoalchemy2 import Geometry, func
from geoalchemy2.functions import GenericFunction
import app.helpers.point_form
import sys, os, traceback, base64
from app import db
from app.models.point import Point
from app.models.submission import Submission

class SubmissionsController:

    def create(self):
        try:
            json_data = request.get_json()
            # self.__save_image(json_data["submission_id"], json_data["image"])

            submission = Submission.query.filter(Submission.user_id == 1, Submission.submission_id == int(json_data['submission_id'])).first()
            if submission is None:
                submission = self.__make_submission(json_data)
                db.session.add(submission)
            new_point = self.__make_point(json_data, submission)
            db.session.add(new_point)
            db.session.commit()
            return Response(json.dumps({ "status" : "ok", "received_data" : json_data, "point" : str(new_point) })) 
        except Exception as e:
            return Response(json.dumps({ "status" : "error", "error_message" : str(e), "trace" : traceback.format_exc() })), 500



    def __make_point(self, data, submission):
        new_point = Point()
        new_point.name = data["point"]['name']
        new_point.geom = "POINT({} {})".format(data["point"]["latitude"], data["point"]["longitude"])
        new_point.properties = data["point"]["properties"]
        new_point.revised = False;
        new_point.submission_id = submission.id 
        return new_point

    def __make_submission(self, data):
        new_submission = Submission()
        new_submission.submission_id = data["submission_id"]
        new_submission.user_id = 1 
        new_submission.revised = False;
        return new_submission


    def __save_image(self,submission_id, encoded_string):
        directory = "app/uploads/submissions/" + submission_id 
        if not os.path.exists(directory):
            os.makedirs(directory)
        fh = open(directory + "/test.png", "wb")
        fh.write(base64.b64decode(encoded_string))
        fh.close()


