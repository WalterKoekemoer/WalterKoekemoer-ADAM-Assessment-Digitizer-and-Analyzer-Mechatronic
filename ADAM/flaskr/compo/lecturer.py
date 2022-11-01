from flask import (
    Blueprint, flash, render_template, request, redirect, session
)

from flaskr.db import get_db

bp = Blueprint('lecturer', __name__, url_prefix='/lecturer/dashboard')


@bp.route('/assessors', methods=('GET', 'POST'))
def assessors():
    if request.method == 'GET' or request.method == 'POST':
        db = get_db()
        assessors = db.execute(
            'SELECT assessor.id, username, FOS, T, M, completions, sts FROM assessor ' +
            'LEFT JOIN gathering ON gathering.lecturer_id = ? ' +
            'LEFT JOIN participant ON participant.gathering_id = gathering.id ' +
            'WHERE sts = 1 '
            'OR assessor.id = participant.assessor_id', (session['user_id'],),
        ).fetchall()
        print(assessors)
        gatherings = db.execute(
            'SELECT test_module, created, completed, id FROM gathering WHERE gathering.lecturer_id = ? ' +
            'AND completed = NULL',(session['user_id'],),
        ).fetchall()
        
    return render_template('lecturer/dashboard/assessors.html', assessors=assessors, gatherings=gatherings)

@bp.route('/invite', methods=('GET', 'POST'))
def invite():
    if request.method == 'POST':
        db = get_db()
        id = int(request.form['id'])
        room = request.form['room']
        total = request.form['total']
        description = request.form['description']

        error = None
        sts = db.execute(
            'SELECT sts FROM assessor WHERE id = ?', (id,),
        ).fetchall()
        if not sts:
            error = "no such user?"
        elif sts == 0:
            error = "That user was taken just now."
        elif not total.isnumeric():
            error = "Please enter a valid total"
        elif total.__len__() > 3:
            error = "Please enter a valid total"

        if not error:
            if room == "uninvite":
                pass
            elif room.isnumeric():
                db.execute(
                    "INSERT INTO participant (assessor_id, gathering_id, section_description, section_total) VALUES (?, ?, ?, ?)",
                    (id, room, description, int(total)),
                )
                db.execute(
                    'UPDATE assessor SET sts = ? WHERE id = ?', (0,id)
                ).fetchall()
                db.commit()
        else:
            flash(error)
        
    return redirect(request.referrer)

@bp.route('/gatherings', methods=('GET', 'POST'))
def gatherings():
    if request.method == 'POST':
        db = get_db()
        id = int(request.form['id'])
        gatherings = db.execute(
            'SELECT * FROM gathering WHERE id = ?', (id,),
        ).fetchone()
        return render_template('lecturer/dashboard/gatherings.html', gatherings=gatherings)
    return redirect(request.referrer)

@bp.route('/module_results', methods=('GET', 'POST'))
def module_results():
    if request.method == 'POST':
        db = get_db()
        id = int(request.form['id'])
        module_results = db.execute(
            'SELECT SUM(sections_mark)/(gathering.test_total*COUNT(test.id)) AS class_avg ' + 
            ',gathering.created AS created ' + 
            ',gathering.test_date AS test_date ' +
            ',gathering.test_module AS test_module ' +
            ',gathering.test_total AS test_total ' +
            ',gathering.completed AS completed ' + 
            'FROM sections ' + 
            'INNER JOIN test ON test.id = sections.test_id ' +
            'INNER JOIN gathering ON gathering.id = test.gathering_id ' +
            'WHERE gathering.lecturer_id = ? ' + 
            'GROUP BY gathering.id '
            'ORDER BY gathering.created DESC ', (id,),
        ).fetchall()

        return render_template('lecturer/dashboard/module_results.html', module_results=module_results)
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
            'INNER JOIN gathering ON gathering.id = test.gathering_id ' +
            'INNER JOIN participant ON gathering.id = participant.gathering_id ' +
            'INNER JOIN assessor ON assessor.id = participant.assessor_id ' +
            'WHERE gathering.lecturer_id = ? ' + 
            'GROUP BY sections.id, gathering.id ', (id,),
        ).fetchall()

        return render_template('lecturer/dashboard/section_results.html', section_results=section_results)
    return redirect(request.referrer)

