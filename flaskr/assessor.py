from flask import (
    Blueprint, render_template, request, redirect
)

from flaskr.db import get_db

bp = Blueprint('assessor', __name__, url_prefix='/assessor/dashboard')


@bp.route('/scheadule', methods=('GET', 'POST'))
def scheadule():
    if request.method == 'POST':
        db = get_db()
        id = int(request.form['id'])
        scheadules = db.execute(
            'SELECT * FROM gathering INNER JOIN participant ON gathering.id = participant.gathering_id WHERE participant.assessor_id = ?', (1,id)
        ).fetchone()
        return render_template('assessor/dashboard/scheadule.html', scheadules=scheadules)
    return redirect(request.referrer)

@bp.route('/status', methods=('GET', 'POST'))
def status():
    if request.method == 'POST':
        db = get_db()
        status = request.form['status']
        id = int(request.form['id'])
        if id:
            if status == "Available":
                db.execute(
                    'UPDATE assessor SET sts = ? WHERE id = ?', (1,id)
                ).fetchone()
            elif status == "Busy":
                db.execute(
                    'UPDATE assessor SET sts = ? WHERE id = ?', (0,id)
                ).fetchone()
            db.commit()
    return redirect(request.referrer)