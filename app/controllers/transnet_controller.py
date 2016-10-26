from datetime import datetime

from flask import render_template
from flask import request, json, Response

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

    def export(self):
        if (not request.args.get('bounds') and
                not request.args.get('ids')):
            return Response(json.dumps([]), mimetype='application/json')

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
        relations = self.export()

        headers = {
            'Content-Type': 'application/xml',
            'Content-Disposition': 'attachment; filename=relations.xml'
        }

        presenter = RelationsPresenter(relations)
        return Response(presenter.as_xml_element(), headers=headers)

    def export_csv(self):
        relations = self.export()

        headers = {
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment; filename=CSV-%s.zip' % datetime.now()
        }

        csv_writer = CSVWriter(relations)
        return Response(csv_writer.publish(), headers=headers)

    def export_countries(self):
        if not request.args.get("countries"):
            return Response(json.dumps([]), mimetype='application/json')

        voltages = None
        bounds_parts = None
        countries = request.args.get("countries").split(',')

        return TransnetRelation.get_filtered_relations(bounds_parts, voltages, countries, None)

    def export_countries_xml(self):
        relations = self.export_countries()

        headers = {
            'Content-Type': 'application/xml',
            'Content-Disposition': 'attachment; filename=relations.xml'
        }

        presenter = RelationsPresenter(relations)
        return Response(presenter.as_xml_element(), headers=headers)

    def export_countries_csv(self):
        relations = self.export_countries()

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
            request.args.get("countries").split(',')))
