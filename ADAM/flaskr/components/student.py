from flask import (
    Blueprint, render_template, request, redirect
)

from flaskr.db import get_db

bp = Blueprint('student', __name__, url_prefix='/results/dashboard')


@bp.route('/student_results/<int:id>', methods=('GET', 'POST'))
def student_results(id):
    if request.method == 'GET':
        db = get_db()
        student_results = db.execute(
            'SELECT SUM(sections_mark)/(gatherings.test_total*COUNT(test.id)) AS student_grade ' + 
            'CONCAT(student_number.n1,student_number.n2,student_number.n3,student_number.n4,student_number.n5,student_number.n6,student_number.n7,student_number.n8) as SN ' +
            ',gatherings.created AS created ' + 
            ',gatherings.title AS title ' +
            ',gatherings.test_date AS test_date ' +
            ',gatherings.test_module AS test_module ' +
            ',gatherings.test_total AS test_total ' +
            ',gatherings.completed AS completed ' + 
            'FROM sections ' + 
            'INNER JOIN test ON test.id = sections.test_id ' +
            'INNER JOIN student_number ON test.student_number_id = student_number.id ' +
            'INNER JOIN gatherings ON gatherings.id = test.gathering_id ' +
            'WHERE gatherings.lecturer_id = ? ' + 
            'GROUP BY test.id ', (id,),
        ).fetchall()

        return render_template('assessor/dashboard/student_results.html', student_results=student_results)
    return redirect(request.referrer)