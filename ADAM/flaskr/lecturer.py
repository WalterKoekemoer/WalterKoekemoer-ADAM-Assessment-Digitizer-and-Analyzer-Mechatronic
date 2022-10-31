from flask import (
    Blueprint, render_template, request, redirect
)

from flaskr.db import get_db

bp = Blueprint('lecturer', __name__, url_prefix='/lecturer/dashboard')


@bp.route('/assessors', methods=('GET', 'POST'))
def assessors():
    if request.method == 'POST':
        db = get_db()
        assessors = db.execute(
            'SELECT * FROM assessors',
        ).fetchone()
        return render_template('assessor/dashboard/assessors.html', assessors=assessors)
    return redirect(request.referrer)

@bp.route('/gatherings', methods=('GET', 'POST'))
def gatherings():
    if request.method == 'POST':
        db = get_db()
        id = int(request.form['id'])
        gatherings = db.execute(
            'SELECT * FROM gatherings WHERE id = ?', (id,)
        ).fetchone()
        return render_template('assessor/dashboard/gatherings.html', gatherings=gatherings)
    return redirect(request.referrer)

@bp.route('/module_results', methods=('GET', 'POST'))
def module_results():
    if request.method == 'POST':
        db = get_db()
        id = int(request.form['id'])
        module_results = db.execute(
            'SELECT SUM(sections_mark)/(gatherings.test_total*COUNT(test.id)) AS class_avg ' + 
            ',gatherings.created AS created ' + 
            ',gatherings.title AS title ' +
            ',gatherings.test_date AS test_date ' +
            ',gatherings.test_module AS test_module ' +
            ',gatherings.test_total AS test_total ' +
            ',gatherings.completed AS completed ' + 
            'FROM sections ' + 
            'INNER JOIN test ON test.id = sections.test_id ' +
            'INNER JOIN gatherings ON gatherings.id = test.gathering_id ' +
            'WHERE gatherings.lecturer_id = ? ' + 
            'GROUP BY gatherings.id '
            'ORDER BY gatherings.created DESC ', (id,)
        ).fetchall()

        return render_template('assessor/dashboard/module_results.html', module_results=module_results)
    return redirect(request.referrer)

@bp.route('/section_results', methods=('GET', 'POST'))
def section_results():
    if request.method == 'POST':
        db = get_db()
        id = int(request.form['id'])
        
        section_results = db.execute(
            'SELECT SUM(sections_mark)/(participant.section_total*COUNT(sections_mark)) as section_average ' +
            ', assessor.username as Assessor ' +
            ', participant.section_description as description ' + 
            'FROM sections ' + 
            'INNER JOIN test ON test.id = sections.test_id ' +
            'INNER JOIN gatherings ON gatherings.id = test.gathering_id ' +
            'INNER JOIN participant ON gatherings.id = participant.gathering_id ' +
            'INNER JOIN assessor ON assessor.id = participant.assessor_id ' +
            'WHERE gatherings.lecturer_id = ? ' + 
            'GROUP BY sections.id, gatherings.id ', (id,)
        ).fetchall()

        return render_template('assessor/dashboard/section_results.html', section_results=section_results)
    return redirect(request.referrer)

