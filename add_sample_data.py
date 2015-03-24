import random
from app import GisApp, db
import app.models.point
import app.models.powerline


for x in range(0, 1000):
    lat = random.uniform(46.0, 53.0)
    lng = random.uniform(8.0, 15.0)
    print("{}: {} - {}".format(x, lat, lng))
    geometry = "POINT({} {})".format(lat, lng)
    new_point = app.models.point.Point(name="sample_name_{}".format(x), geom=geometry)
    db.session.add(new_point)
    db.session.commit()
