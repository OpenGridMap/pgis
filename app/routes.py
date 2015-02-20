from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import app, db
from app.models.point import Point
from app.helpers.point_add_form import PointAddForm
from app.controllers.points_controller import PointsController

@app.route('/')
@app.route('/index')
def index():
	return render_template('map.html')


@app.route('/points')
def points():
	controller = PointsController()
	return controller.index()
	

@app.route('/admin')
def admin():
	return render_template('admin/index.html')

@app.route('/admin/points')
def admin_points():
	points = Point.query.all()
	return render_template('admin/points/index.html', points=points)

@app.route('/admin/points/add')
def admin_points_add():	
	form = PointAddForm() 
	return render_template('admin/points/add.html', form=form)

@app.route('/admin/points/create', methods=['POST'])
def admin_points_create():
	form = PointAddForm() 
	if form.validate_on_submit():
		geometry = "POINT({} {})".format(form.latitude.data, form.longitude.data)
		new_point = Point(name=form.name.data, geom=geometry)
		db.session.add(new_point)
		db.session.commit()
		return redirect(url_for('admin_points'))
	return 'Error'

@app.route('/admin/points/delete/<id>', methods=['GET'])
def admin_points_delete(id):
	point = Point.query.get(id)
	db.session.delete(point)
	db.session.commit()
	return redirect(url_for('admin_points'))
