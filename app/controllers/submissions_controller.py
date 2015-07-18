from app.models.point import Point
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from geoalchemy2 import Geometry, func
from geoalchemy2.functions import GenericFunction
import app.helpers.point_form
import sys, os, traceback, base64
from app import db

class SubmissionsController:

    def create(self):
        try:
            json_data = request.get_json()
            # self.__save_image(json_data["submission_id"], json_data["image"])
            point = self.__make_point(json_data["point"])
            return Response(json.dumps({ "status" : "ok", "received_data" : json_data, "point" : str(point) })) 
        except Exception as e:
            return Response(json.dumps({ "status" : "error", "error_message" : str(e), "trace" : traceback.format_exc() })), 500



    def __make_point(self, point_data):
        new_point = app.models.point.Point()
        new_point.name = point_data['name']
        new_point.geom = "POINT({} {})".format(point_data["latitude"], point_data["longitude"])
        new_point.properties = point_data["properties"]
        return new_point


    def __save_image(self,submission_id, encoded_string):
        directory = "app/uploads/submissions/" + submission_id 
        if not os.path.exists(directory):
            os.makedirs(directory)
        fh = open(directory + "/test.png", "wb")
        fh.write(base64.b64decode(encoded_string))
        fh.close()


