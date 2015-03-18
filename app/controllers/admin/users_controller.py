from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.user_form
import app.models.user

class UsersController:

    def index(self):
        return render_template('admin/users/index.html')

    def new(self):
        form = app.helpers.user_form.UserForm() 
        return render_template('admin/users/new.html', form=form)

    def create(self):
        return ''

    def edit(self, id):
        return render_template('admin/users/edit.html')

    def update(self, id):
        return render_template('admin/users/index.html')
