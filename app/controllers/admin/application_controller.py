from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response

class ApplicationController:
    def index(self):
        return render_template('admin/index.html')

    def login(self):
        session["next"] = request.args.get("next")
        session["redirect_back"] = True if request.args.get("redirect_back") else False
        return render_template('admin/login.html')
