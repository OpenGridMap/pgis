from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app.models.powerline import Powerline

class PowerlinesController:
	def index(self):
		powerlines = list(map(lambda powerline: powerline.serialize(), Powerline.query.all()))
		return Response(json.dumps(powerlines),  mimetype='application/json')