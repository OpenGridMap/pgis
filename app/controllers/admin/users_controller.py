from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.user_form
import app.models.user

class UsersController:

    def index(self):
        page = int(request.args.get('page') or 1)
        users = app.models.user.User.query.paginate(page)
        return render_template('admin/users/index.html', users=users)

    def new(self):
        form = app.helpers.user_form.UserForm() 
        return render_template('admin/users/new.html', form=form)

    def create(self):
        form = app.helpers.user_form.UserForm() 
        if form.validate_on_submit():
                new_user = app.models.user.User(email=form.email.data, action_permissions=form.action_permissions.data)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('admin_users'))
        return 'Error'

    def edit(self, id):
        user = app.models.user.User.query.get(id)
        form = app.helpers.user_form.UserForm(None, user)
        return render_template('admin/users/edit.html', form=form, user=user)

    def update(self, id): 
        user = app.models.user.User.query.get(id)
        form = app.helpers.user_form.UserForm(request.form, obj=user) 
        if form.validate_on_submit():
            user.action_permissions = form.action_permissions.data
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('admin_users'))
    
    def delete(self, id): 
        user = app.models.user.User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_users'))
