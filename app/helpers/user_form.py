from app import GisApp
from flask.ext.wtf import Form
from wtforms import StringField, FloatField, SelectMultipleField
from wtforms.widgets import CheckboxInput, html_params, HTMLString 
from wtforms.validators import DataRequired

class ListWidget(object):
    """
    Renders a list of fields as a `ul` or `ol` list.
    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.
    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """
    def __init__(self, html_tag='ul', prefix_label=True):
        assert html_tag in ('ol', 'ul')
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ['<%s class="list-group" %s>' % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append('<li class="list-group-item">%s %s</li>' % (subfield.label, subfield()))
            else:
                html.append('<li class="list-group-item">%s %s</li>' % (subfield(), subfield.label))
        html.append('</%s>' % self.html_tag)
        return HTMLString(''.join(html))

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

def action_permission_tuples():
    action_permission_tuples = []
    action_permissions = GisApp.config.get('ACTION_PERMISSIONS')

    for action_permission in action_permissions:
        action_permission_tuples.append((action_permission, action_permission))

    return action_permission_tuples

class UserForm(Form):
    email 	            = StringField('email', validators=[DataRequired()])
    action_permissions  = MultiCheckboxField('action_permissions', choices=action_permission_tuples())
