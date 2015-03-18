from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.user_form
import app.models.user

class UsersController:

    def index(self):
        users = app.models.user.User.query.all()
        return render_template('admin/users/index.html', users=users)

    def new(self):
        form = app.helpers.user_form.UserForm() 
        return render_template('admin/users/new.html', form=form)

    def create(self):
        form = app.helpers.user_form.UserForm() 
        if form.validate_on_submit():
                new_user = app.models.user.User(email=form.email.data)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('admin_users'))
        return 'Error'

    def edit(self, id):
        return render_template('admin/users/edit.html')

    def update(self, id): 
        return render_template('admin/users/index.html')
    
    def delete(self, id): 
        user = app.models.user.User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_users'))
