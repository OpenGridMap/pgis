from flask.ext.wtf import Form
from wtforms import StringField, FloatField, TextAreaField
from wtforms.validators import DataRequired

class PowerlineForm(Form):
    latlngs 		= StringField('latlngs', validators=[DataRequired()])
    properties          = TextAreaField('properties') 
