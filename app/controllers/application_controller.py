from flask import render_template

import app.helpers.point_form
from app.models.transnet_country import TransnetCountry


class ApplicationController:
    def index(self):
        point_form = app.helpers.point_form.PointForm()
        voltages = TransnetCountry.get_voltages()
        world = TransnetCountry.get_countries()
        return render_template('map.html', point_form=point_form, voltages=voltages, world=world)

    def update(self):
        return None

    def page500(self):
        return render_template('500.html')

    def page403(self):
        return render_template('403.html')
