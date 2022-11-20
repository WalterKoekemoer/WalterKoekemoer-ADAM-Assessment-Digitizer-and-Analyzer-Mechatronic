from flask import (
    Blueprint, flash, render_template, request, redirect, session, url_for
)

from flaskr.db import get_db
import pandas as pd

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
        elif not description:
            error = "Please enter description"
        elif not total:
            error = "Please enter a sub-total"
        elif not total.isnumeric():
            error = "Please enter a valid total"
        elif total.__len__() > 3:
            error = "Please enter a valid total"

        if not error:
            if room == "uninvite":
                flash("uninvited!",id)
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
            flash(error,id)
        
    return redirect(request.referrer)

@bp.route('/gatherings', methods=('GET', 'POST'))
def gatherings():
    if request.method == 'POST':
        db = get_db()
        gatherings = db.execute(
            'SELECT * FROM gathering WHERE lecturer_id = ? ORDER BY created', (session['user_id'],),
        ).fetchall()

    return render_template('lecturer/dashboard/gatherings.html', gatherings=gatherings)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        db = get_db()
        test_module = request.form['test_module']
        test_date = request.form['test_date']
        test_total = int(request.form['test_total'])
        cursor=db.cursor()

        cursor.execute(
            "INSERT INTO gathering (test_module, test_date, test_total, lecturer_id) VALUES (?, ?, ?, ?)",
            (test_module, test_date, test_total, session['user_id']),
        )

        cursor.execute(
            "INSERT INTO test (gathering_id) VALUES (?)",
            (cursor.lastrowid,),
        )

        
        df = pd.read_excel(request.files.get('file'))
        df = df['Student Numbers'].astype(str)
        n = pd.DataFrame(dtype='uint8')
        n['n1'] = df.str[0:1]
        n['n2'] = df.str[1:2]
        n['n3'] = df.str[2:3]
        n['n4'] = df.str[3:4]
        n['n5'] = df.str[4:5]
        n['n6'] = df.str[5:6]
        n['n7'] = df.str[6:7]
        n['n8'] = df.str[7:8]
        n['test_id'] = cursor.lastrowid
        n.to_sql('student_number', con=db, if_exists='append', method='multi', index=False)
            
        db.commit()

        gatherings = db.execute(
            'SELECT * FROM gathering WHERE lecturer_id = ? ORDER BY created DESC', (session['user_id'],),
        ).fetchall()

    return render_template('lecturer/dashboard/gatherings.html', gatherings=gatherings)

@bp.route('/join', methods=('GET', 'POST'))
def join():
    pass

@bp.route('/assess', methods=('GET', 'POST'))
def assess():
    if request.method == 'POST':
        session['token'] = int(request.form['gathering_id'])
        session['type'] = "Lecturer"

        return redirect(url_for('adam.identify'))
    else:
        db = get_db()
        gatherings = db.execute(
            'SELECT * FROM gathering WHERE lecturer_id = ? ORDER BY created DESC', (session['user_id'],),
        ).fetchall()

        return render_template('lecturer/dashboard/gatherings.html', gatherings=gatherings)

@bp.route('/complete', methods=('GET', 'POST'))
def complete():
    pass

@bp.route('/remove', methods=('GET', 'POST'))
def remove():
    pass

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

