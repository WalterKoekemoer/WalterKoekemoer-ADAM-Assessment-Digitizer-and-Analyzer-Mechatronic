from flask import (
    Blueprint, render_template, request, redirect
)

from flaskr.db import get_db

bp = Blueprint('lecturer', __name__, url_prefix='/results/dashboard')


@bp.route('/student_results/<int:id>', methods=('GET', 'POST'))
def student_results(id):
    if request.method == 'GET':
        db = get_db()
        student_results = db.execute(
            'SELECT SUM(sections_mark)/(gatherings.test_total*COUNT(test.id)) AS student_grade ' + 
            'CONCAT(test.n1,test.n2,test.n3,test.n4,test.n5,test.n6,test.n7,test.n8) as student_number ' +
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
            'GROUP BY test.id ', (id,)
        ).fetchall()

        return render_template('assessor/dashboard/student_results.html', student_results=student_results)
    return redirect(request.referrer)