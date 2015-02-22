from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response

class PowerlinesController:
	def index(self):
		return render_template('admin/powerlines/index.html')