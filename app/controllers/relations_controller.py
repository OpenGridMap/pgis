from app.models.relation import Relation
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from geoalchemy2 import Geometry, func
from geoalchemy2.functions import GenericFunction
from app import db
from sqlalchemy.sql import text
from app.models.powerline import Powerline
from flask_sqlalchemy import get_debug_queries

class RelationsController:
    def index(self):
        if request.args.get('bounds') is None:
            return Response(json.dumps([]), mimetype='application/json')

        bounds_parts = request.args.get("bounds").split(',')
        relations = Relation.with_points_and_lines_in_bounds(bounds_parts)

        return Response(json.dumps(relations), mimetype='application/json')
