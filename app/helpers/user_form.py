from flask.ext.wtf import Form
from wtforms import StringField, FloatField, SelectMultipleField
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import DataRequired

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class UserForm(Form):
    email 	            = StringField('email', validators=[DataRequired()])
    action_permissions  = MultiCheckboxField('action_permissions', choices=[("foo", "bar")])
