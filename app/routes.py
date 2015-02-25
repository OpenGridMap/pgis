from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import GisApp, db
import app.models.point
import app.models.powerline
import app.controllers.application_controller
import app.controllers.points_controller
import app.controllers.powerlines_controller
import app.controllers.admin.application_controller
import app.controllers.admin.points_controller
import app.controllers.admin.powerlines_controller

@GisApp.route('/')
@GisApp.route('/index')
def index():
	controller = app.controllers.application_controller.ApplicationController()
	return controller.index()


@GisApp.route('/points')
def points():
	controller = app.controllers.points_controller.PointsController()
	return controller.index()

@GisApp.route('/powerlines', methods=['GET'])
def powerlines():
	controller = app.controllers.powerlines_controller.PowerlinesController()
	return controller.index()	

@GisApp.route('/admin')
def admin():
	controller = app.controllers.admin.application_controller.ApplicationController()
	return controller.index()

@GisApp.route('/admin/points')
def admin_points():
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.index()

@GisApp.route('/admin/points/new')
def admin_points_add():	
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.new()

@GisApp.route('/admin/points/create', methods=['POST'])
def admin_points_create():
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.create()

@GisApp.route('/admin/points/delete/<id>', methods=['GET'])
def admin_points_delete(id):
	controller = app.controllers.admin.points_controller.PointsController()
	return controller.delete(id)

@GisApp.route('/admin/powerlines')
def admin_powerlines():
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.index()

@GisApp.route('/admin/powerlines/new')
def admin_powerlines_new():
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.new()

@GisApp.route('/admin/powerlines/create', methods=['POST'])
def admin_powerlines_create():
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.create()

@GisApp.route('/admin/powerlines/edit/<id>', methods=['GET'])
def admin_powerlines_edit(id):
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.edit(id)

@GisApp.route('/admin/powerlines/update/<id>', methods=['POST'])
def admin_powerlines_update(id):
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.update(id)

@GisApp.route('/admin/powerlines/delete/<id>', methods=['GET'])
def admin_powerlines_delete(id):
	controller = app.controllers.admin.powerlines_controller.PowerlinesController()
	return controller.delete(id)
