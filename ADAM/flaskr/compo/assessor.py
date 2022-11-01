from flask import (
    Blueprint, render_template, request, redirect, session
)

from flaskr.db import get_db

bp = Blueprint('assessor', __name__, url_prefix='/assessor/dashboard')


@bp.route('/scheadule', methods=('GET', 'POST'))
def scheadule():
    if request.method == 'GET':
        db = get_db()
        scheadules = db.execute(
            'SELECT lecturer.username AS Lec, gathering.test_module AS Mod, gathering.created AS Crt, participant.readed_msg FROM participant ' + 
            'INNER JOIN gathering ON gathering.id = participant.gathering_id ' +
            'INNER JOIN lecturer ON gathering.lecturer_id = lecturer.id ' +
            'WHERE participant.assessor_id = ?' +
            'ORDER BY gathering.created DESC', (session['user_id'],),
        ).fetchall()

    return render_template('assessor/dashboard/scheadule.html', scheadules=scheadules)

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
                )
            elif status == "Busy":
                db.execute(
                    'UPDATE assessor SET sts = ? WHERE id = ?', (0,id),
                )
            db.commit()
            
    return redirect(request.referrer)