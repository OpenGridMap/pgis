from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.powerline_form
from app.models.powerline import Powerline

class PowerlinesController:
	def index(self):
		powerlines = Powerline.query.all()
		return render_template('admin/powerlines/index.html', powerlines=powerlines)

	def new(self):
		form = app.helpers.powerline_form.PowerlineForm() 
		return render_template('admin/powerlines/new.html', form=form)

	def create(self):
		form = app.helpers.powerline_form.PowerlineForm() 
		if form.validate_on_submit():
			geometry = "LINESTRING({})".format(form.latlngs.data)
			new_powerline = app.models.powerline.Powerline(geom=geometry)
			db.session.add(new_powerline)
			db.session.commit()
			return redirect(url_for('admin_powerlines'))
		return 'Error'

	def edit(self, id):
		powerline = app.models.powerline.Powerline.query.get(id)
		form = app.helpers.powerline_form.PowerlineForm()
		form.latlngs.data = powerline.linestring()
		return render_template('admin/powerlines/edit.html', form=form, id=id)

	def update(self, id):
		powerline = app.models.powerline.Powerline.query.get(id)
		form = app.helpers.powerline_form.PowerlineForm(obj=powerline) 
		if form.validate_on_submit():
			geometry = "LINESTRING({})".format(form.latlngs.data)
			powerline.geom = geometry
			db.session.add(powerline)
			db.session.commit()
			return redirect(url_for('admin_powerlines'))
		return 'Error'

	def delete(self, id):
		powerline = app.models.powerline.Powerline.query.get(id)
		db.session.delete(powerline)
		db.session.commit()
		return redirect(url_for('admin_powerlines'))