from app.models.relation import Relation
from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from geoalchemy2 import Geometry, func
from geoalchemy2.functions import GenericFunction
from app import db
from sqlalchemy.sql import text
from app.models.powerline import Powerline
from flask_sqlalchemy import get_debug_queries
from app.presenters.relations_presenter import RelationsPresenter

class RelationsController:
    def index(self):
        if request.args.get('bounds') is None:
            return Response(json.dumps([]), mimetype='application/json')

        bounds_parts = request.args.get("bounds").split(',')
        relations = Relation.with_points_and_lines_in_bounds(bounds_parts)

        return Response(json.dumps(relations), mimetype='application/json')

    def export(self):
        if (request.args.get('bounds') is None and
                request.args.get('ids') is None):
            return Response(json.dumps([]), mimetype='application/json')

        if request.args.get('bounds') is not None:
            bounds_parts = request.args.get("bounds").split(',')
            relations = Relation.with_points_and_lines_in_bounds(bounds_parts)

        if request.args.get('ids') is not None:
            relations_ids = request.args.get("ids").split(',')
            relations = Relation.relations_for_export(relations_ids)

        headers = {
            'Content-Type': 'application/osm',
            'Content-Disposition': 'attachment; filename=relations.xml.osm'
        }

        presenter = RelationsPresenter(relations)

        return Response(presenter.as_osm_xml(), headers=headers)
