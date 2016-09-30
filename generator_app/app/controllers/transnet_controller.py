from flask import request, json, Response

from app.models.transnet_relation import TransnetRelation
from app.utils.cim_writer import CimWriter


class TransnetController:
    def __init__(self):
        pass

    def export_cim(self):
        if (not request.args.get('bounds') and
                not request.args.get('ids')):
            return Response(json.dumps([]), mimetype='application/json')

        relations = None
        map_centroid = None
        if request.args.get('bounds') is not None:
            bounds_parts = request.args.get("bounds").split(',')
            relations, map_centroid = TransnetRelation.with_points_and_lines_in_bounds(bounds_parts)

        if request.args.get('ids') is not None:
            relations_ids = request.args.get("ids").split(',')
            relations, map_centroid = TransnetRelation.relations_for_export(relations_ids)

        headers = {
            'Content-Type': 'application/xml',
            'Content-Disposition': 'attachment; filename=cim.xml'
        }

        presenter = None

        cim_writer = CimWriter(relations, map_centroid)
        cim_writer.publish('/home/epezhman/Projects/pgis/generator_app')

        return Response(presenter.as_xml_element(), headers=headers)
