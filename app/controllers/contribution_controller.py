from flask import request, json, Response

from app.models.transnet_lines_missing_data import TransnetPowerLineMissingData
from app.models.transnet_station_missing_data import TransnetPowerStationMissingData


class ContributionController:
    def get_lines(self):
        if not request.args.get('bounds'):
            return Response(json.dumps([]), mimetype='application/json')

        bounds_parts = request.args.get("bounds").split(',')
        general_filter = request.args.get("general").split(',') if request.args.get("general") else []
        lines_filter = request.args.get("lines").split(',') if request.args.get("lines") else []

        lines = TransnetPowerLineMissingData.get_filtered_lines(bounds_parts, general_filter, lines_filter)

        return Response(json.dumps(lines), mimetype='application/json')

    def get_stations(self):
        if not request.args.get('bounds'):
            return Response(json.dumps([]), mimetype='application/json')

        bounds_parts = request.args.get("bounds").split(',')
        general_filter = request.args.get("general").split(',') if request.args.get("general") else []
        stations_filter = request.args.get("stations").split(',') if request.args.get("stations") else []

        stations = TransnetPowerStationMissingData.get_filtered_stations(bounds_parts, general_filter, stations_filter)

        return Response(json.dumps(stations), mimetype='application/json')
