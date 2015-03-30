from flask.ext.wtf import Form
from wtforms import StringField, FloatField
from wtforms.validators import DataRequired

class PointForm(Form):
    name 		= StringField('name', validators=[DataRequired()])
    latitude	= FloatField('latitude', validators=[DataRequired()])
    longitude	= FloatField('longitude', validators=[DataRequired()])

    @property
    def geom(self):
        return "POINT({} {})".format(self.latitude.data, self.longitude.data)

    def populate_obj(self, point):
        point.name = self.name.data
        point.geom = self.geom 
