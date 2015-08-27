from flask import render_template, flash, redirect, abort, session, url_for, request, g, json, Response
from app import db
import app.helpers.powerline_form
from app.models.powerline import Powerline

class PowerlinesController:
    def index(self):
        page = int(request.args.get('page') or 1)
        powerlines = Powerline.query.paginate(page)
        return render_template('admin/powerlines/index.html', powerlines=powerlines)

    def new(self):
        form = app.helpers.powerline_form.PowerlineForm() 
        return render_template('admin/powerlines/new.html', form=form)

    def create(self):
        form = app.helpers.powerline_form.PowerlineForm() 
        if form.validate_on_submit():
            new_powerline = app.models.powerline.Powerline()
            form.populate_obj(new_powerline)
            db.session.add(new_powerline)
            db.session.commit()
            if "redirect_back" in session:
                del session["redirect_back"]
                return redirect(url_for('index', bounds=",".join([str(c) for c in list(new_powerline.shape().bounds)]) ))
            else:
                return redirect(url_for('admin_powerlines'))
        return 'Error'

    def edit(self, id):
        powerline = app.models.powerline.Powerline.query.get(id)
        form = app.helpers.powerline_form.PowerlineForm(None, powerline)
        form.properties.data = json.dumps(form.properties.data) if form.properties.data else ""
        if request.args.get("redirect_back"):
            session["redirect_back"] = True
        return render_template('admin/powerlines/edit.html', form=form, powerline=powerline)

    def update(self, id):
        powerline = app.models.powerline.Powerline.query.get(id)
        form = app.helpers.powerline_form.PowerlineForm(request.form, powerline) 
        if form.validate_on_submit():
            form.populate_obj(powerline)
            db.session.add(powerline)
            db.session.commit()
            if "redirect_back" in session:
                del session["redirect_back"]
                return redirect(url_for('index', bounds=",".join([str(c) for c in list(powerline.shape().bounds)]) ))
            else:
                return redirect(url_for('admin_powerlines'))
        return 'Error'

    def delete(self, id):
        powerline = app.models.powerline.Powerline.query.get(id)
        db.session.delete(powerline)
        db.session.commit()
        return redirect(url_for('admin_powerlines'))
