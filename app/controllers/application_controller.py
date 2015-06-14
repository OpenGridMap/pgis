from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
import app.helpers.point_form

class ApplicationController:
    def index(self):
        point_form = app.helpers.point_form.PointForm() 
        return render_template('map.html', point_form=point_form)

    def update(self):
        return None 

    def page500(self):
        return render_template('500.html') 
    
    def page403(self):
        return render_template('403.html') 
