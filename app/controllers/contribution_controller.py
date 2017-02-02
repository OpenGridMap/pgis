from flask import request, json, Response

from app.models.transnet_lines_missing_data import TransnetPowerLineMissingData


class ContributionController:
    def index(self):
        if not request.args.get('bounds'):
            return Response(json.dumps([]), mimetype='application/json')

        bounds_parts = request.args.get("bounds").split(',')
        lines = TransnetPowerLineMissingData.get_filtered_relations(bounds_parts)

        return Response(json.dumps(lines), mimetype='application/json')
