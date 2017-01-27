import uuid

from flask.ext.wtf import Form
from wtforms import TextAreaField, StringField
from wtforms.validators import DataRequired


class TransnetDownloadUserForm(Form):
    name = StringField('name', validators=[DataRequired()])
    organization = StringField('organization', validators=[DataRequired()])
    purpose = TextAreaField('purpose', validators=[DataRequired()])
    email = StringField('email', )
    url = StringField('url', )

    def populate_obj(self, user):
        user.name = self.name.data
        user.organization = self.organization.data
        user.purpose = self.purpose.data
        user.email = self.email.data
        user.url = self.url.data
        user.uuid = str(uuid.uuid4())
