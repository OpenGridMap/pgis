from datetime import datetime
from os.path import join, dirname

from flask import make_response
from flask import render_template, send_from_directory, jsonify
from flask import request, json, Response

from app.helpers.transnet_download_user_form import TransnetDownloadUserForm
from app.helpers.transnet_export_type_enum import TransnetExportType
from app.models.transnet_download_log import TransnetDownloadLog
from app.models.transnet_download_user import TransnetDownloadUser
from app.models.transnet_relation import TransnetRelation
from app.presenters.relations_presenter import RelationsPresenter
from app.utils.csv_writer import CSVWriter


class TransnetController:
    def index(self):
        if not request.args.get('bounds'):
            return Response(json.dumps([]), mimetype='application/json')
        bounds_parts = request.args.get("bounds").split(',')

        zoom = request.args.get('zoom')

        countries = None
        voltages = None
        if request.args.get("countries"):
            countries = request.args.get("countries").split(',')
        if request.args.get("voltages"):
            voltages = [int(v) for v in request.args.get("voltages").split(',')]

        relations = TransnetRelation.get_filtered_relations(bounds_parts, voltages, countries, zoom)

        return Response(json.dumps(relations), mimetype='application/json')

    def stations_info(self):
        if not request.args.get('relation_id'):
            return Response(json.dumps([]), mimetype='application/json')
        relation_id = request.args.get("relation_id")

        relations = TransnetRelation.get_station_info(relation_id)

        return render_template('stations_info.html', relations=relations)

    def export(self, file_type):
        if (not request.args.get('bounds') and
                not request.args.get('ids')):
            return Response(json.dumps([]), mimetype='application/json')

        if not TransnetDownloadLog.add_log(uuid=request.args.get("token"),
                                           bounds=request.args.get("bounds"),
                                           countries=request.args.get("countries"),
                                           voltages=request.args.get("voltages"),
                                           relations_ids=request.args.get('ids'),
                                           file_type=file_type):
            return make_response('Bad Formatted User Token', 400)

        countries = None
        voltages = None
        if request.args.get("countries"):
            countries = request.args.get("countries").split(',')
        if request.args.get("voltages"):
            voltages = [int(v) for v in request.args.get("voltages").split(',')]

        relations = None
        if request.args.get('bounds') is not None:
            bounds_parts = request.args.get("bounds").split(',')
            relations = TransnetRelation.get_filtered_relations(bounds_parts, voltages, countries, None)

        if request.args.get('ids') is not None:
            relations_ids = request.args.get("ids").split(',')
            relations = TransnetRelation.relations_for_export(relations_ids)

        return relations

    def export_xml(self):
        relations = self.export(TransnetExportType.XML)

        headers = {
            'Content-Type': 'application/xml',
            'Content-Disposition': 'attachment; filename=relations.xml'
        }

        presenter = RelationsPresenter(relations, transnet=True)
        return Response(presenter.as_osm_xml(), headers=headers)

    def export_csv(self):
        relations = self.export(TransnetExportType.CSV)

        headers = {
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment; filename=CSV-%s.zip' % datetime.now()
        }

        csv_writer = CSVWriter(relations)
        return Response(csv_writer.publish(), headers=headers)

    def export_countries(self, file_type):
        if not request.args.get("countries"):
            return Response(json.dumps([]), mimetype='application/json')

        if not TransnetDownloadLog.add_log(uuid=request.args.get("token"),
                                           countries=request.args.get("countries"),
                                           voltages=request.args.get("voltages"),
                                           file_type=file_type):
            return make_response('Bad Formatted User Token', 400)

        voltages = None
        bounds_parts = None
        countries = request.args.get("countries").split(',')
        if request.args.get("voltages"):
            voltages = [int(v) for v in request.args.get("voltages").split(',')]

        return TransnetRelation.get_filtered_relations(bounds_parts, voltages, countries, None)

    def export_countries_xml(self):
        relations = self.export_countries(TransnetExportType.XML)

        headers = {
            'Content-Type': 'application/xml',
            'Content-Disposition': 'attachment; filename=relations.xml'
        }

        presenter = RelationsPresenter(relations, transnet=True)
        return Response(presenter.as_osm_xml(), headers=headers)

    def export_countries_csv(self):
        relations = self.export_countries(TransnetExportType.CSV)

        headers = {
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment; filename=CSV-%s.zip' % datetime.now()
        }

        csv_writer = CSVWriter(relations)
        return Response(csv_writer.publish(), headers=headers)

    def evaluations(self):
        if not request.args.get("countries"):
            return Response(json.dumps([]), mimetype='application/json')

        return render_template('evaluations.html', countries_stats=TransnetRelation.get_evaluations(
            request.args.get("countries").split(','), request.args.get("hit_rate")))

    def matlab_scripts(self):
        return send_from_directory(join(dirname(__file__), '../../resources/'), 'matlab.zip')

    def create_download_user(self):
        form = TransnetDownloadUserForm()
        user_uuid = TransnetDownloadUser.create_user(form)
        if user_uuid:
            return jsonify(uuid=user_uuid)
        return jsonify(uuid="Nan")
