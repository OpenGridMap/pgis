import factory
import factory.alchemy
from geoalchemy2.elements import WKTElement 
from app.models.powerline import Powerline
from app import db

class PowerlineFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Powerline
        sqlalchemy_session = db.session

    properties = { "foo" : "bar", "tags" : [] } 
    geom = WKTElement("LINESTRING(48.11 10.1,59.12 10.15)")
