from flask import render_template, redirect, url_for, request

from app import db
from app.models.transnet_download_user import TransnetDownloadUser


class TransnetUsersController:
    def index(self):
        page = int(request.args.get('page') or 1)
        users = TransnetDownloadUser.query.paginate(page)
        return render_template('admin/transnet_users/index.html', users=users)

    def delete(self, id):
        user = TransnetDownloadUser.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('transnet_users'))
