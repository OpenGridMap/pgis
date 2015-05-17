from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response

class ApplicationController:
    def index(self):
        return render_template('map.html')

    def update(self):
        return None 

    def page500(self):
        return render_template('500.html') 
    
    def page403(self):
        return render_template('403.html') 
