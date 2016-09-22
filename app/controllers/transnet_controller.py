from flask import request, json, Response
from geoalchemy2 import Geography, Geometry
from geoalchemy2 import func
from sqlalchemy import cast

from app.models.transnet_powerline import TransnetPowerline


class TransnetController:
    def index(self):
        if request.args.get('bounds') is None:
            return Response(json.dumps([]), mimetype='application/json')
        bounds_parts = request.args.get("bounds").split(',')

        powerlines = TransnetPowerline.query.filter(
            func.ST_Intersects(
                func.ST_MakeEnvelope(
                    bounds_parts[1],
                    bounds_parts[0],
                    bounds_parts[3],
                    bounds_parts[2]
                ),
                cast( TransnetPowerline.geom, Geography)

            )
        ).all()

        #powerlines = TransnetPowerline.query.all()

        powerlines = list(map(lambda powerline: powerline.serialize(), powerlines))

        return Response(json.dumps(powerlines), mimetype='application/json')