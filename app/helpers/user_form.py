from flask.ext.wtf import Form
from wtforms import StringField, FloatField
from wtforms.validators import DataRequired

class UserForm(Form):
    email 	= StringField('email', validators=[DataRequired()])
