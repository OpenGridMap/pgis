from flask import json
from flask.ext.wtf import Form
from wtforms import StringField, FloatField, TextAreaField
from wtforms.validators import DataRequired

class PowerlineForm(Form):
    latlngs 		= StringField('latlngs', validators=[DataRequired()])
    properties          = TextAreaField('properties') 


    def populate_obj(self, obj):
        geometry = "LINESTRING({})".format(self.latlngs.data)
        obj.geom = geometry
        obj.properties = json.loads(self.properties.data) if self.properties.data else ""
        return self 
