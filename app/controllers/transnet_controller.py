from flask import request, json, Response

from app.models.transnet_relation import TransnetRelation
from app.presenters.relations_presenter import RelationsPresenter


class TransnetController:
    def index(self):
        if not request.args.get('bounds'):
            return Response(json.dumps([]), mimetype='application/json')

        bounds_parts = request.args.get("bounds").split(',')
        relations = TransnetRelation.with_points_and_lines_in_bounds(bounds_parts)

        return Response(json.dumps(relations), mimetype='application/json')

    def export(self):
        if (not request.args.get('bounds') and
                not request.args.get('ids')):
            return Response(json.dumps([]), mimetype='application/json')

        relations = None
        if request.args.get('bounds') is not None:
            bounds_parts = request.args.get("bounds").split(',')
            relations = TransnetRelation.with_points_and_lines_in_bounds(bounds_parts)

        if request.args.get('ids') is not None:
            relations_ids = request.args.get("ids").split(',')
            relations = TransnetRelation.relations_for_export(relations_ids)

        headers = {
            'Content-Type': 'application/xml',
            'Content-Disposition': 'attachment; filename=relations.xml'
        }

        presenter = RelationsPresenter(relations)
        return Response(presenter.as_xml_element(), headers=headers)
