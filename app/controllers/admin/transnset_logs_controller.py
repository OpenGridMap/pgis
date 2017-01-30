from flask import render_template, redirect, url_for, request

from app import db
from app.models.transnet_download_log import TransnetDownloadLog


class TransnetLogsController:
    def index(self):
        page = int(request.args.get('page') or 1)
        logs = TransnetDownloadLog.query.order_by(TransnetDownloadLog.download_user_id).paginate(page)
        return render_template('admin/transnet_logs/index.html', logs=logs)

    def delete(self, id):
        log = TransnetDownloadLog.query.get(id)
        db.session.delete(log)
        db.session.commit()
        return redirect(url_for('transnet_logs'))
