from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response

class PowerlinesController:
	def index(self):
		lines = [[[48.1533, 11.5667], [48.1423, 11.5697]], [[48.1533, 11.5667], [48.1123, 11.5197], [48.1323, 11.6097]]]
		return Response(json.dumps(lines),  mimetype='application/json')