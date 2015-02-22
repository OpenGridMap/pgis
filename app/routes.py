from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import GisApp, db
import app.models.point
import app.models.powerline
import app.helpers.point_add_form
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

@GisApp.route('/lines', methods=['GET'])
def lines():
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


