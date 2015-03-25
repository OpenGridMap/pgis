import random
from app import GisApp, db
import app.models.point
import app.models.powerline


for x in range(0, 10000):
    lat = random.uniform(44.0, 56.0)
    lng = random.uniform(6.0, 17.0)
    print("{}: {} - {}".format(x, lat, lng))
    geometry = "POINT({} {})".format(lat, lng)
    new_point = app.models.point.Point(name="sample_name_{}".format(x), geom=geometry)
    db.session.add(new_point)
db.session.commit()
