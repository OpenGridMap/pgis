from app.models.point import Point
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from geoalchemy2 import Geometry, func
from geoalchemy2.functions import GenericFunction
import app.helpers.point_form
import base64
import sys
import os
from app import db

class SubmissionsController:

    def create(self):
        try:
            json_data = request.get_json()
            # self.save_image(json_data["submission_id"], json_data["image"])
            new_point = app.models.point.Point()
            return Response(json.dumps({ "status" : "ok", "received_data" : json_data })) 
        except Exception as e:
            return Response(json.dumps({ "status" : "error", "error_message" : str(e) })), 500


    def save_image(self,submission_id, encoded_string):
        directory = "app/uploads/submissions/" + submission_id 
        if not os.path.exists(directory):
            os.makedirs(directory)
        fh = open(directory + "/test.png", "wb")
        fh.write(base64.b64decode(encoded_string))
        fh.close()


