from flask import json
from flask.ext.wtf import Form
from wtforms import StringField, FloatField, TextAreaField, HiddenField
from wtforms.validators import DataRequired

class PointForm(Form):
    merge_with    = HiddenField('merge_with', default=None)
    latitude	= FloatField('latitude', validators=[DataRequired()])
    longitude	= FloatField('longitude', validators=[DataRequired()])
    properties  = TextAreaField('properties') 

    @property
    def geom(self):
        return "POINT({} {})".format(self.latitude.data, self.longitude.data)

    def populate_obj(self, point):
        point.geom          = self.geom 
        point.properties    = json.loads(self.properties.data) if self.properties.data else {}
        point.revised       = True
        point.approved      = True

