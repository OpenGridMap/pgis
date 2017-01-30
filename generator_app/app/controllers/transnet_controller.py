from datetime import datetime

from flask import make_response
from flask import request, json, Response

from app.models.transnet_download_log import TransnetDownloadLog
from app.models.transnet_relation import TransnetRelation
from app.utils.cim_writer import CimWriter
from app.utils.transnet_export_type_enum import TransnetExportType


class TransnetController:
    def __init__(self):
        pass

    def export_cim(self):
        if (not request.args.get('bounds') and
                not request.args.get('ids')):
            return Response(json.dumps([]), mimetype='application/json')

        if not TransnetDownloadLog.add_log(uuid=request.args.get("token"),
                                           countries=request.args.get("countries"),
                                           voltages=request.args.get("voltages"),
                                           relations_ids=request.args.get("ids"),
                                           bounds=request.args.get('bounds'),
                                           file_type=TransnetExportType.CIM):
            return make_response('Bad Formatted User Token', 400)

        countries = None
        voltages = None
        if request.args.get("countries"):
            countries = request.args.get("countries").split(',')
        if request.args.get("voltages"):
            voltages = [int(v) for v in request.args.get("voltages").split(',')]

        relations = None
        map_centroid = None
        if request.args.get('bounds') is not None:
            bounds_parts = request.args.get("bounds").split(',')
            relations, map_centroid = TransnetRelation.with_points_and_lines_in_bounds(bounds_parts, voltages,
                                                                                       countries)

        if request.args.get('ids') is not None:
            relations_ids = request.args.get("ids").split(',')
            relations, map_centroid = TransnetRelation.relations_for_export(relations_ids)

        headers = {
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment; filename=CIM-%s.zip' % datetime.now()
        }

        cim_writer = CimWriter(relations, map_centroid)

        return Response(cim_writer.publish(), headers=headers)

    def export_cim_countries(self):
        if not request.args.get("countries"):
            return Response(json.dumps([]), mimetype='application/json')

        if not TransnetDownloadLog.add_log(uuid=request.args.get("token"),
                                           countries=request.args.get("countries"),
                                           voltages=request.args.get("voltages"),
                                           relations_ids=request.args.get("ids"),
                                           file_type=TransnetExportType.CIM):
            return make_response('Bad Formatted User Token', 400)

        voltages = None
        bounds_parts = None
        countries = request.args.get("countries").split(',')
        if request.args.get("voltages"):
            voltages = [int(v) for v in request.args.get("voltages").split(',')]

        relations, map_centroid = TransnetRelation.with_points_and_lines_in_bounds(bounds_parts, voltages,
                                                                                   countries)

        if request.args.get('ids') is not None:
            relations_ids = request.args.get("ids").split(',')
            relations, map_centroid = TransnetRelation.relations_for_export(relations_ids)

        headers = {
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment; filename=CIM-%s.zip' % datetime.now()
        }

        cim_writer = CimWriter(relations, map_centroid)

        return Response(cim_writer.publish(), headers=headers)
