from flask import request, json, Response

from app.models.transnet_lines_missing_data import TransnetPowerLineMissingData
from app.models.transnet_station_missing_data import TransnetPowerStationMissingData


class ContributionController:
    def get_lines(self):
        if not request.args.get('bounds'):
            return Response(json.dumps([]), mimetype='application/json')

        bounds_parts = request.args.get("bounds").split(',')
        lines = TransnetPowerLineMissingData.get_filtered_lines(bounds_parts)

        return Response(json.dumps(lines), mimetype='application/json')

    def get_stations(self):
        if not request.args.get('bounds'):
            return Response(json.dumps([]), mimetype='application/json')

        bounds_parts = request.args.get("bounds").split(',')
        stations = TransnetPowerStationMissingData.get_filtered_stations(bounds_parts)

        return Response(json.dumps(stations), mimetype='application/json')
