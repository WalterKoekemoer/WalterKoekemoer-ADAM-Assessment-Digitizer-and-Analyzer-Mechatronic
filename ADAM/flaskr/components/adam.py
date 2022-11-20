from flask import (
    Blueprint, render_template, request, session, redirect, url_for
)

from flaskr.db import get_db

bp = Blueprint('adam', __name__, url_prefix='/adam')


@bp.route('/identify', methods=('GET', 'POST'))
def identify():
    availables = {}
    return render_template('adam/actuators/identify.html',availables=availables)

@bp.route('/back', methods=('GET', 'POST'))
def back():
    if session['type'] == "Lecturer":
        return redirect(url_for('lecturer.assessors'))
    elif session['type'] == "Lecturer":
        return redirect(url_for('assessor.scheadule'))
    else:
        return render_template(request.referrer)


@bp.route('/scan', methods=('GET', 'POST'))
def scan():
    real_scan = request.files['real_scan']
    real_students = request.files['real_students']
    # session['token']
    # session['type']
    return {"message":"success"}